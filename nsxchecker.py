#!/usr/bin/env python
import gevent.monkey
gevent.monkey.patch_all()


import argparse
import gevent.pool
import json
import math
import requests
import sys
import traceback
from requests.auth import HTTPBasicAuth

# Change this if you want to make more concurrent requests
pool = gevent.pool.Pool(50)


class NsxChecker(object):

    def __init__(self, controller, password, quiet=False):
        self.url = 'https://%s:%s' % (controller, '443')
        self.auth = HTTPBasicAuth('admin', args.password)
        self.fail = 0.0
        self.quiet = quiet
        self.reqs = []
        self.success = 0.0
        self.total = 0.0

    def request(self, method, url, body=None, content_type='application/json'):
        headers = {'Content-Type': content_type}
        endpoint = "%s%s" % (self.url, url)
        if method == 'GET':
            r = requests.get(endpoint, auth=self.auth, data=body,
                             headers=headers, verify=False)
        elif method == 'POST':
            r = requests.post(endpoint, auth=self.auth, data=body,
                              headers=headers, verify=False)
        if r.raise_for_status():
            return "%s to %s got unexpected response code: %d (content = '%s')" % (method,
                                                                                   endpoint,
                                                                                   r.status_code,
                                                                                   r.json())
        return r.json()

    def get_lswitch(self, network):
        url = ("/ws.v1/lswitch?_page_length=1000&fields=*&tag=%s&"
               "tag_scope=neutron_net_id") % (network)
        result = self.request('GET', url)
        try:
            uuid = result['results'][0]['uuid']
        except IndexError:
            uuid = network
        return uuid

    def get_lports(self, lswitch):
        url = ("/ws.v1/lswitch/%s/lport?_page_length=1000&fields=*"
               "&relations=VirtualInterfaceConfig") % (lswitch)
        result = self.request('GET', url)
        lports = []
        if result:
            for port in result['results']:
                lport = {}
                lport['uuid'] = port['uuid']
                try:
                    lport['mac'] = port['_relations'][
                        'VirtualInterfaceConfig']['attached_mac']
                except KeyError:
                    continue
                lports.append(lport)
            return lports

    def can_haz_traffic(self, lport, smac, dmac):
        url = "/ws.v1/lswitch/%s/lport/%s/traceflow" % (
            self.lswitch, lport)
        data = json.dumps({'dst_mac': dmac, 'src_mac': smac, 'eth_type': 2048,
                           'frame_size': 128, 'timeout': 2000})

        result = self.request('POST', url, data)
        trace = [obv['type'] for obv in result['observations']]
        return ('TraceflowObservationDelivered' in trace)

    def check_port(self, lport):
        mac = self.macs[0]
        self.check_macs(lport, mac)

    def check_port_full(self, lport):
        for mac in self.macs:
            self.check_macs(lport, mac)

    def check_macs(self, lport, mac):
        if lport['mac'] != mac:
            port_test = self.can_haz_traffic(lport['uuid'], lport['mac'], mac)
            if not self.quiet:
                print "%s -> %s: %s" % (lport['mac'], mac, port_test)
            if port_test:
                self.success = self.success + 1
            else:
                self.fail = self.fail + 1
            self.total = self.total + 1


def percentage(part, whole):
    return int(100 * float(part) / float(whole))


def main(args):
    nsxchecker = NsxChecker(args.controller, args.password, args.quiet)
    nsxchecker.lswitch = nsxchecker.get_lswitch(args.network)
    nsxchecker.lports = nsxchecker.get_lports(nsxchecker.lswitch)
    nsxchecker.macs = [lport['mac'] for lport in nsxchecker.lports]
    if len(nsxchecker.lports) <= 1:
        print "No ports to check!"
        return 0
    if not nsxchecker.quiet:
        print "%s ports on this network. " % len(nsxchecker.lports)
    if not nsxchecker.lports:
        if not nsxchecker.quiet:
            print "Nothing found!"
        quit()
    if args.full:
        out_string = "A full check will is %s src/dests."
        print out_string % int(math.pow(len(nsxchecker.lports), 2))
        pool.map(nsxchecker.check_port_full, nsxchecker.lports)
    else:
        pool.map(nsxchecker.check_port, nsxchecker.lports)
    if not nsxchecker.quiet:
        print "-" * 40

    fail_percent = percentage(nsxchecker.fail, nsxchecker.total)
    success_percent = percentage(nsxchecker.success, nsxchecker.total)
    if success_percent > 0:
        out_string = "%s percent successful (network ID: %s)"
        print out_string % (success_percent, args.network)
    if fail_percent > 0:
        out_string = "%s percent fail (network ID: %s)"
        print out_string % (fail_percent, args.network)
    return 0

if __name__ == '__main__':
    description = "nsxchecker injects traffic between ports through NSX API"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--quiet', action='store_true',
                        help='show mac address pairs')
    parser.add_argument('--controller',
                        help='controller')
    parser.add_argument('--password',
                        help='password')
    parser.add_argument('--full', action='store_true',
                        help='check every single port with every other port '
                             '(cartesian product)')
    parser.add_argument('--network',
                        help='neutron network or nsx lswitch id')
    args = parser.parse_args()
    ret = 69
    try:
        ret = main(args)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "*** Exception:"
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
    sys.exit(ret)
