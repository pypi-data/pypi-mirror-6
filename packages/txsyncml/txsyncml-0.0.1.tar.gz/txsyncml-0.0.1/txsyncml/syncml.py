class SyncMLEngine(object):

    def process(self, doc):
        self.process_header(doc.get_header())
        self.process_body(doc.get_body())

    def process_header(self, header):
        print header

    def process_body(self, body):
        print body
        print body.get_alerts()
