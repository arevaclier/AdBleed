from os.path import *
from scapy.all import *

class Discovery:
    'Discovery class handles automatic discovery of Pi-hole.'
    __hosts = []
    
    def __init__(self):
        # Open host file
        fileName = join(dirname(__file__), "../hosts.txt")
        # Strip comments from the file and store result in __hosts separated by \n
        cleanHosts = ""
        with open(fileName, "r") as file:
            for line in file:
                if not ( line.strip().startswith("#") or line.strip().startswith(";") ):
                    add = line.strip()
                    if not len(add) == 0 :
                        cleanHosts += add + "\n"
        # Separate hosts into array of strings per host
        Discovery.__hosts = cleanHosts.split('\n')
        # Remove last line if the file ended with an empty line
        if Discovery.__hosts[-1] == '' :
            Discovery.__hosts.pop()

    # Resolves urls in __hosts through the system specified DNS
    # The most frequent IP of each DNS server is saved and the overall most frequent IP is selected.
    # If the relative frequency of that IP was more than 75% of the __hosts, it is returned.
    # Otherwise None is returned.
    def getPi(self):
        ips = []
        dns = self.getDNS()
        maxIP = []
        
        for server in dns:
            for url in Discovery.__hosts:
                answer = sr1(IP(dst=server)/UDP(dport=53)/DNS(rd=1,qd=DNSQR(qname=url)),verbose=0)
                ips.append(answer[DNS].an[answer[DNS].ancount-1].rdata) # Only save the IP
            # Save the most frequent ip for every DNS server
            mostFreqElement = max(set(ips), key=ips.count)
            maxIP.append([mostFreqElement, ips.count(mostFreqElement)])
            ips = []
    
        # Select the most frequent element of max
        maxFreq = 0
        piIP = None
        for ip in maxIP:
            if maxFreq < maxIP[1]:
                piIP = maxIP[0]
                maxFreq = maxIP[1]
        
        if maxFreq/len(dns) > 0.75 :
            return piIP
        else :
            return None

    
    # Returns list of DNS servers from /etc/resolv.conf
    def getDNS(self):
        servers = []
        # Todo: only select for the current domain
        with open("/etc/resolv.conf", "r") as file :
            for line in file:
                if line.strip().startswith("nameserver "):
                    servers.append(line.strip().split(" ")[1])
        return servers

    pass
