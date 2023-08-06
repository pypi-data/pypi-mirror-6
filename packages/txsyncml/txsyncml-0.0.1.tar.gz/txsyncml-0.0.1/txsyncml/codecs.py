# -*- test-case-name: txsyncml.tests.test_codecs -*-
from twisted.internet.defer import succeed

from txsyncml.wbxml import xml2wbxml, wbxml2xml


class XmlCodec(object):

    content_type = 'application/vnd.syncml+xml'

    def encode(self, data):
        if isinstance(data, unicode):
            data = data.encode('utf-8')
        return succeed(data)

    def decode(self, data):
        return succeed(data)


class WbXmlCodec(XmlCodec):

    content_type = 'application/vnd.syncml+wbxml'

    def encode(self, data):
        d = super(WbXmlCodec, self).encode(data)
        d.addCallback(xml2wbxml)
        return d

    def decode(self, data):
        d = wbxml2xml(data)
        d.addCallback(super(WbXmlCodec, self).decode)
        return d


codecs = [
    XmlCodec(),
    WbXmlCodec(),
]


def get_codec(request):
    # NOTE: I'm ignoring content-type in the format
    #       'application/json; charset=utf-8'. Burn that bridge when
    #       I get there.
    [content_type] = request.requestHeaders.getRawHeaders('Content-Type')
    for codec in codecs:
        if codec.content_type == content_type:
            return codec
