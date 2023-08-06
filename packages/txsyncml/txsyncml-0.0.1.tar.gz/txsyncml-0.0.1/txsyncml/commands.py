# -*- test-case-name: txsyncml.tests.test_commands -*-
import base64

from twisted.words.xish.domish import Element


class SyncMLError(Exception):
    pass


class SyncMLElement(object):

    allowed_children = []

    def __init__(self, name, value, ns=None, children=[]):
        self.name = name
        self.value = value
        self.ns = ns
        self.children = []
        for child in children:
            self.add_child(child)

    def add_child(self, child):
        if child.__class__ not in self.allowed_children:
            raise SyncMLError('Child %r not allowed for %r.' % (
                child.__class__, self.__class__))
        self.children.append(child)

    def build(self):
        element = self.build_children(self.build_root())
        if self.value is not None:
            element.addContent(self.value)
        return element

    def build_root(self):
        return Element((self.ns, self.name))

    def build_children(self, element):
        for child in self.children:
            element.addChild(child.build())
        return element

    def to_xml(self):
        return self.build().toXml()

    def find(self, child_name):
        if not isinstance(child_name, basestring):
            child_name = child_name.__name__
        return [child for child in self.children if child.name == child_name]


class SessionID(SyncMLElement):

    @classmethod
    def create(cls, session_id):
        return cls('SessionID', unicode(session_id))


class MsgID(SyncMLElement):

    @classmethod
    def create(cls, msg_id):
        return cls('MsgID', unicode(msg_id))


class LocURI(SyncMLElement):

    @classmethod
    def create(cls, loc_uri):
        return cls('LocURI', unicode(loc_uri))


class Target(SyncMLElement):

    allowed_children = [LocURI]

    @classmethod
    def create(cls, loc_uri):
        return cls('Target', None, children=[LocURI.create(loc_uri)])


class Source(SyncMLElement):

    allowed_children = [LocURI]

    @classmethod
    def create(cls, loc_uri):
        return cls('Source', None, children=[LocURI.create(loc_uri)])


class Type(SyncMLElement):

    @classmethod
    def create(cls, auth_type):
        return cls('Type', auth_type, ns='syncml:metinf')


class Next(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('Next', unicode(value))


class Last(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('Last', unicode(value))


class Anchor(SyncMLElement):

    allowed_children = [Last, Next]

    @classmethod
    def create(cls, last, next):
        return cls('Anchor', None, ns='syncml:metinf', children=[
            Last.create(last),
            Next.create(next),
        ])


class MaxMsgSize(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('MaxMsgSize', unicode(value), ns='syncml:metinf')


class Meta(SyncMLElement):

    allowed_children = [Type, Anchor, MaxMsgSize]

    @classmethod
    def create(cls, children=[]):
        return cls('Meta', None, children=children)


class Data(SyncMLElement):

    @classmethod
    def create(cls, content):
        return cls('Data', unicode(content))


class Cred(SyncMLElement):

    allowed_children = [Meta, Data]

    @classmethod
    def create(cls, username, password, auth_type='syncml:auth-basic'):
        return cls('Cred', None, children=[
            Meta.create([Type.create(auth_type)]),
            Data.create(base64.b64encode('%s:%s' % (username, password)))
        ])


class VerDTD(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('VerDTD', unicode(value))


class VerProto(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('VerProto', unicode(value))


class SyncHdr(SyncMLElement):

    allowed_children = [
        VerDTD,
        VerProto,
        SessionID,
        MsgID,
        Target,
        Source,
        Cred,
        Meta,
    ]

    @classmethod
    def create(cls, session_id, msg_id,
               target=None, source=None, cred=None, meta=None, ver_dtd='1.1',
               ver_proto='SyncML/1.1'):

        children = [
            VerDTD.create(ver_dtd),
            VerProto.create(ver_proto),
            SessionID.create(session_id),
            MsgID.create(msg_id)
        ]

        if target is not None:
            children.append(target)

        if source is not None:
            children.append(source)

        if cred is not None:
            children.append(cred)

        if meta is not None:
            children.append(meta)

        return cls('SyncHdr', None, children=children)


class CmdID(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('CmdID', unicode(value))


class Item(SyncMLElement):

    allowed_children = [Target, Source, Meta]

    @classmethod
    def create(cls, target, source, anchor):
        return cls('Item', None, children=[
            Target.create(target),
            Source.create(source),
            Meta.create(children=[anchor])])


class Alert(SyncMLElement):

    allowed_children = [CmdID, Data, Item]

    @classmethod
    def create(cls, cmd_id, code, items=[]):
        return cls('Alert', None, children=[
            CmdID.create(cmd_id),
            Data.create(code),
        ] + items)


class MsgRef(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('MsgRef', unicode(value))


class CmdRef(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('CmdRef', unicode(value))


class Cmd(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('Cmd', unicode(value))


class TargetRef(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('TargetRef', unicode(value))


class SourceRef(SyncMLElement):

    @classmethod
    def create(cls, value):
        return cls('SourceRef', unicode(value))


class Status(SyncMLElement):

    allowed_children = [
        CmdID,
        MsgRef,
        CmdRef,
        Cmd,
        TargetRef,
        SourceRef,
        Data,
    ]

    @classmethod
    def create(cls, cmd_id, msg_ref, cmd_ref, cmd,
               target_ref, source_ref, code):
        return cls('Status', None, children=[
            CmdID.create(cmd_id),
            MsgRef.create(msg_ref),
            CmdRef.create(cmd_ref),
            Cmd.create(cmd),
            TargetRef.create(target_ref),
            SourceRef.create(source_ref),
            Data.create(code),
        ])


class SyncBody(SyncMLElement):

    allowed_children = [Alert, Meta, Status]

    @classmethod
    def create(cls, alerts=[], statuses=[]):
        return cls('SyncBody', None, children=(alerts + statuses))


class SyncML(SyncMLElement):

    allowed_children = [SyncHdr, SyncBody]

    @classmethod
    def create(cls, header=None, body=None):
        return cls('SyncML', None, children=filter(None, [header, body]))

    def get_header(self):
        return self.find(SyncHdr)[0]

    def get_body(self):
        return self.find(SyncBody)[0]
