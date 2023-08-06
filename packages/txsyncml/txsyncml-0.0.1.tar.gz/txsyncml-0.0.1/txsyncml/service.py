from twisted.application import strports
from twisted.internet import reactor
from twisted.python import usage
from twisted.web import server

from txsyncml.resource import TxSyncMLResource

DEFAULT_PORT = 'tcp:8080'


class Options(usage.Options):
    """Command line args when run as a twistd plugin"""
    # TODO other args
    optParameters = [["endpoint", "e", DEFAULT_PORT,
                      "Endpoint for txsyncml server to listen on"]]


def makeService(options):
    resource = TxSyncMLResource(reactor=reactor)
    site = server.Site(resource)
    return strports.service(options['endpoint'], site)
