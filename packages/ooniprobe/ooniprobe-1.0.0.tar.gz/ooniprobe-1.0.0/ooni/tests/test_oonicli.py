import sys

from twisted.internet import base
from twisted.trial import unittest

base.DelayedCall.debug = True

from ooni.oonicli import runWithDirector

class TestRunDirector(unittest.TestCase):
    def test_run_with_director(self):
        sys.argv = ['', 'blocking/http_requests', '-u', 'http://google.com/']
        #runWithDirector()

