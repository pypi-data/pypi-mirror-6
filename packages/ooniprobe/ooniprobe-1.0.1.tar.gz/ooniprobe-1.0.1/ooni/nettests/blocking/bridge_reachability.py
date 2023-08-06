# -*- encoding: utf-8 -*-
import random
import string
import subprocess
from distutils.spawn import find_executable

from twisted.python import usage
from twisted.internet import defer, reactor, error

import txtorcon

from ooni.utils import log
from ooni import nettest

class UsageOptions(usage.Options):
    optParameters = [['timeout', 't', 120,
                      'Specify the timeout after which to consider the Tor bootstrapping process to have failed'],
                    ]

class BridgeReachability(nettest.NetTestCase):
    name = "Bridge Reachability"
    author = "Arturo Filastò"
    version = "0.1"

    usageOptions = UsageOptions

    inputFile = ['file', 'f', None,
                 'File containing bridges to test reachability for. '
                 'They should be one per line IP:ORPort or '
                 'TransportType IP:ORPort (ex. obfs2 127.0.0.1:443)']

    requiredOptions = ['file']

    def setUp(self):
        self.tor_progress = 0
        self.timeout = int(self.localOptions['timeout'])

        self.report['timeout'] = self.timeout
        self.report['transport_name'] = 'vanilla'
        self.report['tor_progress'] = 0
        self.report['tor_progress_tag'] = None
        self.report['tor_progress_summary'] = None
        self.report['bridge_address'] = None

        self.bridge = self.input
        if self.input.startswith('Bridge'):
            self.bridge = self.input.replace('Bridge ', '')
        self.pyobfsproxy_bin = find_executable('obfsproxy')
    
    def postProcessor(self, measurements):
        if 'successes' not in self.summary:
            self.summary['successes'] = []
        if 'failures' not in self.summary:
            self.summary['failures'] = []

        details = {
            'address': self.report['bridge_address'],
            'transport_name': self.report['transport_name'],
            'tor_progress': self.report['tor_progress']
        }
        if self.report['success']:
            self.summary['successes'].append(details)
        else:
            self.summary['failures'].append(details)
        return self.report

    def displaySummary(self, summary):
        successful_count = {}
        failure_count = {}
        def count(results, counter):
            for result in results:
                if result['transport_name'] not in counter:
                    counter[result['transport_name']] = 0
                counter[result['transport_name']] += 1
        count(summary['successes'], successful_count)
        count(summary['failures'], failure_count)

        working_bridges = ', '.join(["%s %s" % (x['transport_name'], x['address']) for x in summary['successes']])
        failing_bridges = ', '.join(["%s %s (at %s%%)" % (x['transport_name'], x['address'], x['tor_progress']) for x in summary['failures']])

        print "Total successes: %d" % len(summary['successes'])
        print "Total failures: %d" % len(summary['failures'])

        for transport, count in successful_count.items():
            print "%s successes: %d" % (transport.title(), count)
        for transport, count in failure_count.items():
            print "%s failures: %d" % (transport.title(), count)

        print "Working bridges: %s" % working_bridges
        print "Failing bridges: %s" % failing_bridges

    def test_full_tor_connection(self):
        def getTransport(address):
            """
            If the address of the bridge starts with a valid c identifier then
            we consider it to be a bridge.
            Returns:
                The transport_name if it's a transport.
                None if it's not a obfsproxy bridge.
            """
            transport_name = address.split(' ')[0]
            transport_name_chars = string.ascii_letters + string.digits
            if all(c in transport_name_chars for c in transport_name):
                return transport_name
            else:
                return None

        config = txtorcon.TorConfig()
        config.ControlPort = random.randint(2**14, 2**16)
        config.SocksPort = random.randint(2**14, 2**16)
        
        transport_name = getTransport(self.bridge)
        if transport_name and self.pyobfsproxy_bin:
            config.ClientTransportPlugin = "%s exec %s managed" % (transport_name, self.pyobfsproxy_bin)
            self.report['transport_name'] = transport_name
            self.report['bridge_address'] = self.bridge.split(' ')[1]
        elif transport_name and not self.pyobfsproxy_bin:
            log.err("Unable to test bridge because pyobfsproxy is not installed")
            self.report['success'] = None
            return
        else:
            self.report['bridge_address'] = self.bridge.split(' ')[0]

        config.Bridge = self.bridge
        config.UseBridges = 1
        config.save()

        def updates(prog, tag, summary):
            log.msg("%s: %s%%" % (self.bridge, prog))
            self.report['tor_progress'] = int(prog)
            self.report['tor_progress_tag'] = tag
            self.report['tor_progress_summary'] = summary

        d = txtorcon.launch_tor(config, reactor, timeout=self.timeout,
                                progress_updates=updates)
        @d.addCallback
        def setup_complete(proto):
            try:
                proto.transport.signalProcess('TERM')
            except error.ProcessExitedAlready:
                proto.transport.loseConnection()
            log.msg("Successfully connected to %s" % self.bridge)
            self.report['success'] = True

        @d.addErrback
        def setup_failed(failure):
            log.msg("Failed to connect to %s" % self.bridge)
            self.report['success'] = False

        return d
