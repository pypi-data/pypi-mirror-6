# -*- test-case-name: txsyncml.tests.test_parser -*-

from twisted.web.sux import XMLParser

from txsyncml import commands


class SyncMLParser(XMLParser):

    def __init__(self):
        self.chain = []
        self.registry = []
        self.root = None

    @classmethod
    def parse(cls, data):
        parser = cls()
        parser.connectionMade()
        parser.dataReceived(data)
        return parser.root

    def gotTagStart(self, tagname, attrs):
        klass = getattr(commands, tagname)
        self.chain.append(klass(tagname, None))

    def gotText(self, text):
        # This happens when a DTD is parsed
        if self.chain:
            self.chain[-1].value = text

    def gotDoctype(self, doctype):
        pass

    def gotTagEnd(self, tagname):
        element = self.chain.pop()
        if self.chain:
            parent = self.chain[-1]
            parent.add_child(element)
        else:
            self.root = element
