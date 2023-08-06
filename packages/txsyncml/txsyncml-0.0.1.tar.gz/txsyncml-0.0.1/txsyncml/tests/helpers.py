import pkg_resources

from txsyncml import constants
from txsyncml.commands import (
    SyncML, SyncHdr, Target, Source, Cred, Meta, SyncBody, Item, Alert,
    Anchor, MaxMsgSize)


class FixtureHelper(object):

    def get_fixture(self, fixture_name):
        path = pkg_resources.resource_filename('txsyncml.tests.fixtures',
                                               fixture_name)
        with open(path, 'r') as fp:
            data = fp.read()
        return data


class SyncMLClientHelper(object):

    def build_request(
            self, session_id=1, message_id=1,
            target='http://www.syncml.org/sync-server',
            source='IMEI:493005100592800',
            # Sample from the spec
            username='Bruce2', password='OhBehave',
            metas=[MaxMsgSize.create(5000)],
            last=234, next=276,
            target_db='./contacts/james_bond', source_db='./dev-contacts',
            cmd_id=1, code=constants.SYNC_TWO_WAY):

        header = SyncHdr.create(
            session_id, message_id,
            target=Target.create(target),
            source=Source.create(source),
            cred=Cred.create(username, password),
            meta=Meta.create(metas))
        item = Item.create(target_db, source_db,
                           anchor=Anchor.create(last, next))
        alert = Alert.create(cmd_id, code, items=[item])
        body = SyncBody.create(alerts=[alert])

        return SyncML.create(header=header, body=body)
