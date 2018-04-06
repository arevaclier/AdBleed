from scapy.all import *
from dns import Dns
from discovery import Discovery
from configuration import *

mainText = "Enter the number of the method you want to use:\n\
    1. Pi-hole discovery\n\
    2. ARP Poisoning\n\
    3. DNS Poisoning\n\
    4. Set-up automatic attack\n\
    5. Change settings\n\
    6. Exit\n"

conf = Configuration()
disc = Discovery(conf.getNumberOfHosts(), conf.getSimilarResponses())
dns = None
PiIP = ""
ARPresult = True

def mainCLI():
    while True:
        inp = input(mainText)
        if inp.lower().strip() == "1": # Discovery
            discoveryCLI()
        elif inp.lower().strip() == "2": # ARP Poisoning
            ARPCLI()
        elif inp.lower().strip() == "3": # DNS Poisoning
            DNSCLI()
        elif inp.lower().strip() == "4": # Set-up automatic attack
            automaticCLI()
        elif inp.lower().strip() == "5": # Change settings
            settingsCLI()
        elif inp.lower().strip() == "6": # Exit
            return
        else: # Error
            print("Please only enter a number 1-6\n")

# =========================== Discovery ==============================

def discoveryCLI():
    print("You are about to search for the Pi-hole with settings: ")
    print("   DnsQueryTimeout:  {} ms".format(conf.getDNSQueryTimeout()))
    print("   SimilarResp:      {}%".format(conf.getSimilarResponses()))
    print("   NumberOfHosts:    {}".format(conf.getNumberOfHosts()))
    print("   DNSServer:        {}".format(conf.getDNSsetting()))
    inp = input("Do you want to continue? (Y/n): ")
    
    if inp.lower().strip() == "y" or inp.lower().strip() == "yes" or len(inp.strip()) == 0:
        print("\n")
        PiIP = disc.getPi(conf.getDNSQueryTimeout(), conf.getDNSsetting())
        if not PiIP == None:
            print("Pi-hole was found at " + PiIP + "\nYou can continue with ARP Poisoning")
        else:
            print("No Pi-hole was found")
        return
    elif inp.lower().strip() == "n" or inp.lower().strip() == "no":
        return
    else:
        print("Invalid answer, please answer Y or N\n")
        discoveryCLI()
        return

# ================================= ARP ====================================

def ARPCLI():
    if PiIP == "" or PiIP == None:
        print("IP of the Pi-hole was not set, please run Discovery first.")
        return
    print("You are about to initiate ARP poisoning with settings: ")
    inp = input("Do you want to continue? (Y/n): ")

    if inp.lower().strip() == "y" or inp.lower().strip() == "yes" or len(inp.strip()) == 0:
        print("\n")
        # Call ARP method
        if not ARPresult == True:
            print("Pi-hole was successfully poisoned")
        else:
            print("Poisoning was not successful. Please try again.")
            return
    elif inp.lower().strip() == "n" or inp.lower().strip() == "no":
        return
    else:
        print("Invalid answer, please answer Y or N\n")
        ARPCLI()
        return

# ================================= DNS ===================================

def DNSCLI():
    if not ARPresult:
        print("ARP Poisoning was not completed successfully, please do this first.")
        return
    print("You are about to replace DNS responses of the Pi-hole with settings: ")
    print("   PoisonType:      {}".format(conf.getPoisonType()))
    print("   ReplaceIP:       {}".format(conf.getReplaceIP()))
    print("   SpoofingTimeout: {}".format(conf.getSpoofingTimeout()))
    inp = input("Do you want to continue? (Y/n): ")

    if inp.lower().strip() == "y" or inp.lower().strip() == "yes" or len(inp.strip()) == 0:
        # Ask if we should run in verbose mode
        verbose = input("Do you want to run in verbose mode? (Y/n): ")
        if verbose.lower().strip() == "y" or verbose.lower().strip() == "yes" or len(verbose.strip()) == 0:
            dns = Dns(PiIP, conf.getReplaceIP(), conf.getPoisonType(), True)
        else:
            dns = Dns(PiIP, conf.getReplaceIP(), conf.getPoisonType(), False)
        print("\n")
        # Start spoofing
        dns.spoofer(conf.getSpoofingTimeout())
    elif inp.lower().strip() == "n" or inp.lower().strip() == "no":
        return
    else:
        print("Invalid answer, please answer Y or N\n")
        DNSCLI()
        return

# ============================== Automatic ===================================

def automaticCLI():
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
        automaticCLI()
        return

# =============================== Settings ==============================
          
def settingsCLI():
    print("The settings are currently set as follows:")
    print("1    Discovery: DnsQueryTimeout  ({} ms)".format(conf.getDNSQueryTimeout()))
    print("2    Discovery: SimilarResp      ({}%)".format(conf.getSimilarResponses()))
    print("3    Discovery: NumberOfHosts    ({})".format(conf.getNumberOfHosts()))
    print("4    Discovery: DNSServer        ({})".format(conf.getDNSsetting()))
    print("5    Poisoning: PoisonType       ({})".format(conf.getPoisonType()))
    print("6    Poisoning: ReplaceIP        ({})".format(conf.getReplaceIP()))
    inp = input("\nPlease refer to AdBleed.conf for explanation of the variables. To change a value, enter its number: ")
    var = int(inp)
    if not( int(inp) > 0 and int(inp) < 6):
        print("No valid input, returning to main menu")
        return
    else:
        val = input("To what value do you want to change this value: ")
        if var == 1:
            conf.setDNSQueryTimeout(val)
        elif var == 2:
            conf.setSimilarResponses(val)
        elif var == 3:
            conf.setNumberOfHosts(val)
        elif var == 4:
            conf.setDNSsetting(val)
        elif var == 5:
            conf.setPoisonType(val)
        elif var == 6:
            conf.setReplaceIP(val)
        print("The setting is now set to " + val + "!")
