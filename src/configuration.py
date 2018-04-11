import configparser
import os

class Configuration:
    config = None
    path = None

    networkInterface = ("General", "networkInterface")
    dnsQueryTimeout = ("Discovery", "DnsQueryTimeout")
    similarResponses = ("Discovery", "SimilarResp")
    noOfHosts = ("Discovery", "NumberOfHosts")
    dnsServer = ("Discovery", "DNSServer")
    poisonType = ("Poisoning", "PoisonType")
    replaceIP = ("Poisoning", "ReplaceIP")
    spoofTimeout = ("Poisoning", "SpoofingTimeout")
    arpTargets = ("Poisoning", "ARPtarget")
    arpDelay = ("Poisoning", "ARPdelay")
    arpRefreshDelay = ("Poisoning", "ARPrefreshDelay")

    def __init__(self):
        self.path = os.path.dirname(__file__) + "AdBleed.conf"
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def setConf(self, section, variable, value):
        self.config.set(section, variable, value)
        with open(self.path, "wb") as file:
            self.config.write(file)

    def getConf(self, section, variable):
        return self.config.get(section, variable)

    # |------------------|
    # | Specific get/set |
    # |------------------|

    def getNetworkInterface(self):
        return self.getConf(self.networkInterface[0], self.networkInterface[1])

    def setDNSQueryTimeout(self, value):
        self.setConf(self.dnsQueryTimeout[0], self.dnsQueryTimeout[1], str.encode(value))

    def getDNSQueryTimeout(self):
        return int(self.getConf(self.dnsQueryTimeout[0], self.dnsQueryTimeout[1]))

    def setPoisonType(self, value):
        self.setConf(self.poisonType[0], self.poisonType[1], str.encode(value))

    def getPoisonType(self):
        return self.getConf(self.poisonType[0], self.poisonType[1])

    def setReplaceIP(self, value):
        self.setConf(self.replaceIP[0], self.replaceIP[1], str.encode(value))

    def getReplaceIP(self):
        return self.getConf(self.replaceIP[0], self.replaceIP[1])
    
    def setSimilarResponses(self, value):
        self.setConf(self.similarResponses[0], self.similarResponses[1], str.encode(value))
    
    def getSimilarResponses(self):
        return int(self.getConf(self.similarResponses[0], self.similarResponses[1]))

    def setNumberOfHosts(self, value):
        self.setConf(self.noOfHosts[0], self.noOfHosts[1], str.encode(value))

    def getNumberOfHosts(self):
        return int(self.getConf(self.noOfHosts[0], self.noOfHosts[1]))
    
    def setSpoofingTimeout(self, value):
        self.setConf(self.spoofTimeout[0], self.spoofTimeout[1], str.encode(value))
    
    def getSpoofingTimeout(self):
        return int(self.getConf(self.spoofTimeout[0], self.spoofTimeout[1]))

    def setDNSsetting(self, value):
        self.setConf(self.dnsServer[0], self.dnsServer[1], str.encode(value))
    
    def getDNSsetting(self):
        return self.getConf(self.dnsServer[0], self.dnsServer[1])

    def getARPtarget(self):
        return self.getConf(self.arpTargets[0], self.arpTargets[1])

    def getARPdelay(self):
        return float(self.getConf(self.arpDelay[0], self.arpDelay[1]))

    def getARPhostsRefreshDelay(self):
        return int(self.getConf(self.arpRefreshDelay[0], self.arpRefreshDelay[1]))

