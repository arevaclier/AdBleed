import os

import requests
from scapy.all import *
import signal
from TimeoutException import TimeoutException
import nmap


class Discovery:
    'Discovery class handles automatic discovery of Pi-hole.'
    __hosts = []  # Hosts to check when getPi() is called
    nHosts = 0  # Number of hosts from __hosts to query
    similarResp = 1.0

    def __init__(self, numberOfHosts, similarResponses, hostsURL):
        self.nHosts = numberOfHosts
        self.similarResp = similarResponses / 100

        # Open host file
        fileName = os.path.dirname(__file__) + "/hosts.txt"

        # Strip comments from the file and store result in __hosts separated by \n
        cleanHosts = ""
        with open(fileName, "r") as file:
            for line in file:
                if not (line.strip().startswith("#") or line.strip().startswith(";")):
                    add = line.strip()
                    if not len(add) == 0:
                        cleanHosts += add + "\n"
            file.close()
        # If hostsURL is populated
        if hostsURL:
            internet_hosts = self.get_hosts(hostsURL)
            if internet_hosts != "Error":
                for line in internet_hosts:
                    cleanHosts += line + "\n"
        # Separate hosts into array of strings per host
        Discovery.__hosts = cleanHosts.split('\n')
        # Remove last line if the file ended with an empty line
        if Discovery.__hosts[-1] == '':
            Discovery.__hosts.pop()

    # Resolves urls in __hosts through the system specified DNS
    # The most frequent IP of each DNS server is saved and the overall most frequent IP is selected.
    # If the relative frequency of that IP was more than 75% of the __hosts, it is returned.
    # Otherwise None is returned.
    def getPi(self, timeout, DNSsetting):
        ips = []
        dns = self.getDNS(DNSsetting)
        maxIP = []
        # Set up timer to timeout DNS requests
        signal.signal(signal.SIGALRM, Discovery.timeoutHandler)

        print("Evaluating DNS requests...")
        for server in dns:
            for url in Discovery.__hosts:
                try:
                    signal.setitimer(signal.ITIMER_REAL, float(timeout / 1000))  # Set a timer
                    answer = sr1(IP(dst=server) / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname=url)), verbose=0)
                    signal.setitimer(signal.ITIMER_REAL, 0)  # Reset the timer if we get a response
                    ips.append(answer[DNS].an[answer[DNS].ancount - 1].rdata)  # Only save the IP
                except TimeoutException:
                    ips.append("0.0.0.0")
                    continue

                # No answer in return packet
                except TypeError:
                    break

            # Save the most frequent ip for every DNS server
            mostFreqElement = max(set(ips), key=ips.count)
            maxIP.append([mostFreqElement, ips.count(mostFreqElement)])
            ips = []
        print("Done")

        # Select the most frequent element of max
        maxFreq = 0
        piIP = None
        for ip in maxIP:
            if maxFreq < ip[1] and ip[0] != "0.0.0.0":
                piIP = ip[0]
                maxFreq = ip[1]

        if maxFreq / len(dns) > self.similarResp:
            return piIP
        else:
            return None

    # Returns list of DNS servers from /etc/resolv.conf
    def getDNS(self, DNSsetting):
        servers = []
        if "resolv.conf" in DNSsetting.strip():
            # Obtain servers from /etc/resolv.conf
            with open("/etc/resolv.conf", "r") as file:
                for line in file:
                    if line.strip().startswith("nameserver "):
                        servers.append(line.strip().split(" ")[1])
        elif len(DNSsetting.strip()) >= 9 and len(DNSsetting.strip()) <= 18:  # simple check if it could be an IP
            # Use nmap to see which have port 53 open
            print("Scanning for DNS servers in range " + DNSsetting + "...")
            nm = nmap.PortScanner()
            answer = nm.scan(DNSsetting.strip(), '53')
            for ip in nm.all_hosts():
                if answer['scan'][ip]['tcp'][53]['state'] == 'open':
                    servers.append(ip)
            print("Found " + str(len(servers)) + " possible servers")
        else:
            print("Incorrect DNSSetting, please update AdBleed.conf.")
        return servers

    def timeoutHandler(signum, frame):
        raise TimeoutException("No response from server")

    pass

    # Returns list of banned hosts from an URL
    def get_hosts(self, url):
        try:
            r = requests.get(url, stream=True)
            hosts = []
            for line in r.text.splitlines():
                line.strip()
                if "#" not in line and line is not '':
                    if " " in line:
                        try:
                            line = line.split()
                            hosts.append(line[1])
                        except Exception as e:
                            continue
                    else:
                        hosts.append(line)
            return hosts
        except Exception as e:
            return "Error"
