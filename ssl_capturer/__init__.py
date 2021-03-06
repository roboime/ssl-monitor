import sys
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.protocols import amp

from capturer import SSLV_MulticastProtocol
from transmitter import Push
import transmitter
from pcap import Replayer

class CapturingService(object):
    """"""
    
    def __init__(self, multicast_host, multicast_port, monitor_host, monitor_port, mode='live', pcap=None):
        self.multicast_host = multicast_host
        self.multicast_port = multicast_port
        self.monitor_host = monitor_host
        self.monitor_port = monitor_port
        self.field_id = 'field-1'
        self.monitor_protocol = None
        self.mode = mode
        self.pcap_f = pcap

    def __multicast_handler(self, datagram, address):
        self.monitor_protocol.callRemote(Push, field_id=self.field_id, frame=datagram)



    def __transmitter_connected(self, protocol):
        print "transmitter connected"
        self.monitor_protocol = protocol


    def ready(self):
        self.transmitter = ClientCreator(reactor, amp.AMP).connectTCP(
            self.monitor_host, self.monitor_port).addCallback(self.__transmitter_connected).addErrback(transmitter.error)

        
        # wheter we are replaying from pcap or not
        if self.mode == 'pcap':
            print 'Switching to replay mode'
            pcap = self.pcap_f
            replayer = Replayer(pcap)
            replayer.replay_packets(self.__multicast_handler)
                
        else:
            self.multicast_protocol = SSLV_MulticastProtocol(self.multicast_host, self.__multicast_handler)
            reactor.listenMulticast(self.multicast_port, self.multicast_protocol, listenMultiple=True)
        print "ready"


    def run(self):
        reactor.run()
