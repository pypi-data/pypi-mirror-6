import logging
import gevent
from gevent import socket
from gevent import monkey
from dnslib import A, AAAA, CNAME, MX, RR, TXT
from dnslib import DNSHeader, DNSRecord, QTYPE

monkey.patch_socket()


class DNSServer:
    """
    DNS Server
    """

    AF_INET = 2
    SOCK_DGRAM = 2

    # DNS Aliases
    aliases = {}

    # Callbacks
    before_request = None
    after_request = None

    def __init__(self, host='127.0.01', port=53):
        """
        Construct

        @param   {string}   host  Host
        @param   {integer}  port  UDP Port
        @return  {void}
        """

        # Create Socket
        self.s = socket.socket(self.AF_INET, self.SOCK_DGRAM)

        # Bind To Port
        self.s.bind((host, port))

    def request(self, s, peer, data):
        """
        Handle DNS Request

        @method  request
        @param   {socket}  s      Connection Socket
        @param   {peer}    peer   Peer Connecection
        @param   {mixed}   data   Data
        @return  {void}
        """

        # DNS Request Data
        request = DNSRecord.parse(data)
        id = request.header.id
        qname = request.q.qname
        qtype = request.q.qtype

        logging.info('DNS Request for qname(%s)' % qname)

        # Lookup IP Address
        ip = self.aliases.get(str(qname), False)

        # NOAUTH
        if ip is False:
            reply = DNSRecord(
                        DNSHeader(id=id, qr=1, aa=1, ra=1, rcode=9),
                        q=request.q)
        else:
            reply = DNSRecord(
                        DNSHeader(id=id, qr=1, aa=1, ra=1),
                        q=request.q)

            # Add A Record
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip)))

        # Send To Client
        return self.s.sendto(reply.pack(), peer)

    def start(self):
        """
        Start Server

        @method  start
        @return  {void}
        """

        while True:
            # Recieve DNS Packet
            data, peer = self.s.recvfrom(8192)

            # Before Request Update
            if self.before_request is not None:
                self.aliases = self.before_request()

            # Launch GEvent Co-Routine
            gevent.spawn(self.request, self.s, peer, data)
