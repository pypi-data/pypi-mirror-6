# -*- coding: utf-8 -*-
from twisted.internet.defer import inlineCallbacks
from twisted.web import microdom

from txsyncml.codecs import XmlCodec, WbXmlCodec
from txsyncml.tests.helpers import FixtureHelper
from txsyncml.tests.test_base import TxSyncMLTestCase


class XmlCodecTestCase(TxSyncMLTestCase):

    def setUp(self):
        self.codec = XmlCodec()

    @inlineCallbacks
    def test_encode(self):
        byte_str = yield self.codec.encode('Zoe')
        self.assertEqual(byte_str, 'Zoe')

    @inlineCallbacks
    def test_decode(self):
        byte_str = yield self.codec.decode('Zoe')
        self.assertEqual(byte_str, 'Zoe')


class WbXmlCodecTestCase(TxSyncMLTestCase):

    def setUp(self):
        self.codec = WbXmlCodec()
        self.fixtures = FixtureHelper()

    @inlineCallbacks
    def test_decode(self):
        wbxml = self.fixtures.get_fixture('client_sync_init.wbxml')
        xml = yield self.codec.decode(wbxml)
        dom = microdom.parseXMLString(xml)
        [ver_proto] = dom.getElementsByTagName('VerProto')
        self.assertEqual(ver_proto.firstChild().value, 'SyncML/1.1')

    @inlineCallbacks
    def test_encode(self):
        wbxml = self.fixtures.get_fixture('client_sync_init.wbxml')
        xml = self.fixtures.get_fixture('client_sync_init.xml')
        codec_wbxml = yield self.codec.encode(xml)
        self.assertEqual(wbxml, codec_wbxml)
