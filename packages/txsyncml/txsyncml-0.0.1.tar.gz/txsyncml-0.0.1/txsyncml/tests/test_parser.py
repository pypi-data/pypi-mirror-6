from txsyncml.parser import SyncMLParser
from txsyncml.tests.helpers import FixtureHelper
from txsyncml.tests.test_base import TxSyncMLTestCase


class SyncMLParserTestCase(TxSyncMLTestCase):

    def setUp(self):
        self.fixtures = FixtureHelper()

    def test_header_parsing(self):
        data = self.fixtures.get_fixture('client_sync_init.xml')
        doc = SyncMLParser.parse(data)
        [header] = doc.find('SyncHdr')
        [verdtd] = header.find('VerDTD')
        self.assertEqual(verdtd.value, '1.1')
        [verproto] = header.find('VerProto')
        self.assertEqual(verproto.value, 'SyncML/1.1')
        [session_id] = header.find('SessionID')
        self.assertEqual(session_id.value, '1')
        [msg_id] = header.find('MsgID')
        self.assertEqual(msg_id.value, '1')
        [target] = header.find('Target')
        [target_locuri] = target.find('LocURI')
        self.assertEqual(
            target_locuri.value,
            'http://www.syncml.org/sync-server')
