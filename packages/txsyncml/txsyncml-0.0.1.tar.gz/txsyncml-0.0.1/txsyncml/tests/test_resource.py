from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.web.client import HTTPConnectionPool
from twisted.web import http
from twisted.web import server

from treq import content
from treq.client import HTTPClient

from txsyncml import constants
from txsyncml.codecs import XmlCodec, WbXmlCodec
from txsyncml.resource import TxSyncMLResource
from txsyncml.tests.helpers import FixtureHelper, SyncMLClientHelper
from txsyncml.tests.test_base import TxSyncMLTestCase


class TxSyncMLTestCase(TxSyncMLTestCase):

    content_type = 'application/vnd.syncml+xml'
    codec = XmlCodec

    def setUp(self):
        self.pool = HTTPConnectionPool(reactor, persistent=False)
        self.client = HTTPClient.with_config(
            pool=self.pool, allow_redirects=False, reactor=reactor)
        self.resource = TxSyncMLResource(reactor)
        self.site = server.Site(self.resource)
        self.listener = reactor.listenTCP(0, self.site, interface='localhost')
        self.listener_port = self.listener.getHost().port
        self.fixtures = FixtureHelper()
        self.addCleanup(self.listener.loseConnection)
        self.addCleanup(self.pool.closeCachedConnections)

    def make_url(self, *paths):
        return 'http://localhost:%s/%s' % (
            self.listener_port, ('/'.join(map(str, paths)) + '/'
                                 if paths else ''))

    def request_with_fixture(self, fixture_name, headers={}):
        return self.request(self.fixtures.get_fixture(fixture_name), headers)

    def request(self, data, headers={}):
        default_headers = {
            'Content-Type': [self.content_type],
        }
        default_headers.update(headers)

        d = self.encode_request_data(data)
        d.addCallback(
            lambda data: self.client.post(self.make_url(), data=data,
                                          headers=default_headers))
        return d

    def encode_request_data(self, data):
        return self.codec().encode(data)


class XmlContentTypeTestCase(TxSyncMLTestCase):

    def assertContentType(self, request, content_type):
        headers = request.headers
        [found_content_type] = headers.getRawHeaders('Content-Type')
        self.assertEqual(
            content_type, found_content_type,
            "Content-Types %r and %r don't match." % (
                content_type, found_content_type))

    @inlineCallbacks
    def test_invalid_content_type(self):
        response = yield self.request_with_fixture('client_sync_init.xml', {
            'Content-Type': ['foo'],
        })
        body = yield content(response)
        self.assertEqual(response.code, http.NOT_ACCEPTABLE)
        self.assertContentType(response, 'text/plain')
        self.assertEqual(body, 'Unsupported content-type.')

    @inlineCallbacks
    def test_valid_content_type(self):
        response = yield self.request_with_fixture('client_sync_init.xml')
        self.assertContentType(response, self.content_type)


class WbXmlContentTypeTestCase(XmlContentTypeTestCase):

    content_type = 'application/vnd.syncml+wbxml'
    codec = WbXmlCodec


class ClientSyncTestCase(TxSyncMLTestCase):

    def setUp(self):
        super(ClientSyncTestCase, self).setUp()
        self.syncml = SyncMLClientHelper()

    @inlineCallbacks
    def test_client_init(self):
        # FIXME: this test passes because stuff in the server is hard coded.
        #        revisit this when we're actually parsing stuff.
        syncml = self.syncml.build_request()
        response = yield self.request(syncml.build().toXml())
        body = yield content(response)
        self.assertTrue(str(constants.AUTHENTICATION_ACCEPTED) in body)
