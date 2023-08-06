from twisted.application.service import ServiceMaker

serviceMaker = ServiceMaker(
    'syncml11-server', 'txsyncml.service',
    'SyncML 1.1 server.', 'syncml11-server')
