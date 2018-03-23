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

def mainCLI():
    while True:
        inp = input(mainText)
        if inp.lower().strip() == "1": # Discovery
            discoveryCLI()
        elif inp.lower().strip() == "2": # ARP Poisoning
            continue
        elif inp.lower().strip() == "3": # DNS Poisoning
            continue
        elif inp.lower().strip() == "4": # Set-up automatic attack
            continue
        elif inp.lower().strip() == "5": # Change settings
            settingsCLI()
        elif inp.lower().strip() == "6": # Exit
            return
        else: # Error
            print("Please only enter a number 1-6\n")

def discoveryCLI():
    print("You are about to search for the Pi-hole with settings: ")
    #todo insert settings
    inp = input("Do you want to continue? (Y/n): ")
    
    if inp.lower().strip() == "y" or inp.lower().strip() == "yes" or len(inp.strip()) == 0:
        # Start discovery
        print("Start Pi-hole discovery")
        return
    else:
        print("Invalid answer, please answer Y or N\n")
        return

def settingsCLI():
    print("The settings are currently set as follows:")
    print("1    Discovery: DnsQueryTimeout  ({} ms)".format(conf.getDNSQueryTimeout()))
    print("2    Discovery: SimilarResp      ({}%)".format(conf.getSimilarResponses()))
    print("3    Discovery: NumberOfHosts    ({})".format(conf.getNumberOfHosts()))
    print("4    Poisoning: PoisonType       ({})".format(conf.getPoisonType()))
    print("5    Poisoning: ReplaceIP        ({})".format(conf.getReplaceIP()))
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
            conf.setPoisonType(val)
        elif var == 5:
            conf.setReplaceIP(val)
        print("The setting is now set to " + val + "!")
