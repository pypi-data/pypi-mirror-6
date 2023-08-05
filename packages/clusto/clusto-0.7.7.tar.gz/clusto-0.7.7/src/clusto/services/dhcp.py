from collections import defaultdict
from traceback import format_exc
from struct import unpack
from errno import EINTR
import socket

from clusto.services.config import conf, get_logger
log = get_logger('clusto.dhcp', 'INFO')

import logging
runtime = logging.getLogger('scapy.runtime')
runtime.setLevel(logging.ERROR)
loading = logging.getLogger('scapy.loading')
loading.setLevel(logging.ERROR)

from scapy.all import BOOTP, DHCP, DHCPTypes, DHCPOptions, DHCPRevOptions
from IPy import IP

import clusto

extra = conf('dhcp.extra_options')
extra = dict([(int(k), str(v)) for k, v in extra.items()])
DHCPOptions.update(extra)

for k,v in DHCPOptions.iteritems():
    if type(v) is str:
        n = v
        v = None
    else:
        n = v.name
    DHCPRevOptions[n] = (k,v)

class DHCPRequest(object):
    def __init__(self, packet):
        self.packet = packet
        self.parse()

    def parse(self):
        options = self.packet[DHCP].options
        hwaddr = ':'.join(['%02x' % ord(x) for x in self.packet.chaddr[:6]])

        mac = None
        options = dict([x for x in options if isinstance(x, tuple)])
        if 'client_id' in options:
            # This format is completely nonstandard
            try:
                mac = unpack('>6s', options['client_id'][1:])[0]
                options['client_id'] = ':'.join(['%02x' % ord(x) for x in mac]).lower()
            except:
                log.warning('Unable to parse client_id from %s, ignoring', hwaddr)

        self.type = DHCPTypes[options['message-type']]
        self.hwaddr = hwaddr
        self.options = options

class DHCPResponse(object):
    def __init__(self, type, offerip=None, options={}, request=None):
        self.type = type
        self.offerip = offerip
        self.serverip = socket.gethostbyname(socket.gethostname())
        self.options = options
        self.request = request

    def set_type(self, type):
        self.type = type

    def build(self):
        options = [
            ('message-type', self.type)
        ]
        pxelinux = False
        for k, v in self.options.items():
            if k == 'enabled': continue
            if not k in DHCPRevOptions:
                log.warning('Unknown DHCP option: %s' % k)
                continue
            if k.startswith('pxelinux'):
                pxelinux = True
            if isinstance(v, unicode):
                v = v.encode('ascii', 'ignore')
            options.append((k, v))

        if pxelinux:
            options.append(('pxelinux-magic', '\xf1\x00\x75\x7e'))

        bootp_options = {
            'op': 2,
            'xid': self.request.packet.xid,
            'ciaddr': '0.0.0.0',
            'yiaddr': self.offerip,
            'chaddr': self.request.packet.chaddr,
        }
        if 'tftp_server' in self.options:
            bootp_options['siaddr'] = self.options['tftp_server']
        if 'tftp_filename' in self.options:
            bootp_options['file'] = self.options['tftp_filename']
        for k, v in bootp_options.items():
            if isinstance(v, unicode):
                bootp_options[k] = v.encode('ascii', 'ignore')

        pkt = BOOTP(**bootp_options)/DHCP(options=options)
        #pkt.show()
        return pkt.build()

class DHCPServer(object):
    def __init__(self, bind_address=('0.0.0.0', 67)):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(bind_address)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_id = socket.gethostbyname(socket.gethostname())

    def run(self):
        while True:
            try:
                data, address = self.sock.recvfrom(4096)
            except KeyboardInterrupt:
                break
            except socket.error, e:
                if e.args[0] == EINTR:
                    continue
                log.error(format_exc())
                break
            packet = BOOTP(data)
            request = DHCPRequest(packet)

            log.debug('%s %s' % (request.type, request.hwaddr))

            methodname = 'handle_%s' % request.type
            if hasattr(self, methodname):
                method = getattr(self, methodname)
                try:
                    method(request)
                except:
                    log.error(format_exc())
                    continue

    def send(self, address, data):
        while data:
            bytes = self.sock.sendto(str(data), 0, (address, 68))
            data = data[bytes:]

class ClustoDHCPServer(DHCPServer):
    def __init__(self):
        DHCPServer.__init__(self)
        self.offers = {}
        log.info('Clusto DHCP server starting')

    def handle_request(self, request):
        chaddr = request.packet.chaddr
        if not chaddr in self.offers:
            log.warning('Got a request before sending an offer from %s' % request.hwaddr)
            return
        response = self.offers[chaddr]
        response.type = 'ack'

        self.send('255.255.255.255', response.build())

    def handle_discover(self, request):
        if conf('dhcp.update_ipmi'):
            self.update_ipmi(request)

        attrs = [{
            'key': 'port-nic-eth',
            'subkey': 'mac',
            'number': 1,
            'value': request.hwaddr,
        }]
        server = clusto.get_entities(attrs=attrs)

        if not server:
            return

        if len(server) > 1:
            log.warning('More than one server with address %s: %s' % (request.hwaddr, ', '.join([x.name for x in server])))
            return
        
        server = server[0]

        enabled = server.attrs(key='dhcp', subkey='enabled', merge_container_attrs=True)
        if not enabled or not enabled[0].value:
            log.info('DHCP not enabled for %s' % server.name)
            return

        ips = defaultdict(dict)
        for attr in server.attrs(key='ip'):
            ips[attr.number][attr.subkey] = attr.value

        for num, ip in ips.items():
            if IP(ip['ipstring']).iptype() != 'PRIVATE':
                del ips[num]
        if not ips:
            log.info('No private IP assigned for %s' % server.name)
            return
        
        ip = ips.values().pop()
        ipman = dict([(x.key, x.value) for x in ip['manager'].attrs(subkey='property')])
        #ipman = dict([(x['key'], x['value']) for x in clusto.get_ip_manager(ip).attrs() if x['subkey'] == 'property'])
        ipy = IP('%s/%s' % (ip['ipstring'], ipman['netmask']), make_net=True)

        options = {
            'server_id': self.server_id,
            'lease_time': 3600,
            'renewal_time': 1600,
            'subnet_mask': ipman['netmask'],
            'broadcast_address': ipy.broadcast().strNormal(),
            'router': ipman['gateway'],
            'hostname': server.hostname,
        }

        log.info('Sending offer to %s, options: %s' % (server.name, options))

        for attr in server.attrs(key='dhcp', merge_container_attrs=True):
            options[attr.subkey] = attr.value

        response = DHCPResponse(type='offer', offerip=ip['ipstring'], options=options, request=request)
        self.offers[request.packet.chaddr] = response
        self.send('255.255.255.255', response.build())

    def update_ipmi(self, request):
        attrs = [{
            'key': 'bootstrap',
            'subkey': 'mac',
            'value': request.hwaddr,
        }, {
            'key': 'port-nic-eth',
            'subkey': 'mac',
            'number': 1,
            'value': request.hwaddr,
        }]
        server = clusto.get_entities(attrs=attrs)

        if not server:
            return

        try:
            server = server[0]
            if request.options.get('vendor_class_id', None) == 'udhcp 0.9.9-pre':
                # This is an IPMI request
                #logging.debug('Associating IPMI %s %s' % (request.hwaddr, server.name))
                server.set_port_attr('nic-eth', 1, 'ipmi-mac', request.hwaddr)
            else:
                #logging.debug('Associating physical %s %s' % (requst.hwaddr, server.name))
                server.set_port_attr('nic-eth', 1, 'mac', request.hwaddr)
        except:
            log.error('Error updating server MAC: %s' % format_exc())

