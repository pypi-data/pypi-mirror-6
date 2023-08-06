from base64 import b64encode

from txsyncml import constants
from txsyncml.commands import (
    SyncML, SyncHdr, Target, Source, Cred, Meta, SyncBody, Item, Alert,
    Anchor, Data, Status, Type)
from txsyncml.tests.test_base import TxSyncMLTestCase


class SyncMLElementTestCase(TxSyncMLTestCase):

    def assertXml(self, element, xml_str):
        self.assertEqual(element.to_xml(), xml_str)

    def test_syncml(self):
        self.assertXml(SyncML.create(), '<SyncML/>')

    def test_synchdr(self):
        self.assertXml(
            SyncHdr.create('1', '1'),
            '<SyncHdr>'
            '<VerDTD>1.1</VerDTD>'
            '<VerProto>SyncML/1.1</VerProto>'
            '<SessionID>1</SessionID>'
            '<MsgID>1</MsgID>'
            '</SyncHdr>')

    def test_target(self):
        self.assertXml(
            Target.create('foo'),
            '<Target>'
            '<LocURI>foo</LocURI>'
            '</Target>')

    def test_source(self):
        self.assertXml(
            Source.create('foo'),
            '<Source>'
            '<LocURI>foo</LocURI>'
            '</Source>')

    def test_cred(self):
        self.assertXml(
            Cred.create('foo', 'bar', auth_type='some-algorithm'),
            "<Cred>"
            "<Meta>"
            "<Type xmlns='syncml:metinf'>some-algorithm</Type>"
            "</Meta>"
            "<Data>%s</Data>"
            "</Cred>" % (b64encode("foo:bar")))

    def test_meta(self):
        meta = Meta.create([
            Type.create('syncml:auth-basic'),
        ])

        self.assertXml(
            meta,
            "<Meta>"
            "<Type xmlns='syncml:metinf'>syncml:auth-basic</Type>"
            "</Meta>")

    def test_syncbody(self):
        self.assertXml(
            SyncBody.create(),
            '<SyncBody/>')

    def test_item(self):
        anchor = Anchor.create(234, 276)
        item = Item.create('target', 'source', anchor)
        # print item.children
        self.assertXml(
            item,
            "<Item>"
            "<Target>"
            "<LocURI>target</LocURI>"
            "</Target>"
            "<Source>"
            "<LocURI>source</LocURI>"
            "</Source>"
            "<Meta>"
            "<Anchor xmlns='syncml:metinf'>"
            "<Last>234</Last>"
            "<Next>276</Next>"
            "</Anchor>"
            "</Meta>"
            "</Item>")

    def test_alert(self):
        self.assertXml(
            Alert.create(1, constants.SYNC_REFRESH_FROM_CLIENT),
            "<Alert>"
            "<CmdID>1</CmdID>"
            "<Data>203</Data>"
            "</Alert>")

    def test_anchor(self):
        self.assertXml(
            Anchor.create('last', 'next'),
            "<Anchor xmlns='syncml:metinf'>"
            "<Last>last</Last>"
            "<Next>next</Next>"
            "</Anchor>")

    def test_data(self):
        self.assertXml(
            Data.create(constants.AUTHENTICATION_ACCEPTED),
            '<Data>212</Data>')

    def test_status(self):
        self.assertXml(
            Status.create(1, 2, 3, 'SyncHdr', 'target', 'source',
                          constants.AUTHENTICATION_ACCEPTED),
            "<Status>"
            "<CmdID>1</CmdID>"
            "<MsgRef>2</MsgRef>"
            "<CmdRef>3</CmdRef>"
            "<Cmd>SyncHdr</Cmd>"
            "<TargetRef>target</TargetRef>"
            "<SourceRef>source</SourceRef>"
            "<Data>212</Data>"
            "</Status>")
