import os

from twisted.trial.unittest import TestCase


class TxSyncMLTestCase(TestCase):

    timeout = int(os.environ.get('TXSYNCML_TEST_TIMEOUT', 1))
