import configparser
import os

class Configuration:
    config = None
    path = None

    dnsQueryTimeout = ("Discovery", "DnsQueryTimeout")
    similarResponses = ("Discovery", "SimilarResp")
    noOfHosts = ("Discovery", "NumberOfHosts")
    poisonType = ("Poisoning", "PoisonType")
    replaceIP = ("Poisoning", "ReplaceIP")

    def __init__(self):
        self.path = os.path.dirname(__file__) + "/../AdBleed.conf"
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
    def setDNSQueryTimeout(self, value):
        self.setConf(self.dnsQueryTimeout[0], self.dnsQueryTimeout[1], str.encode(value))

    def getDNSQueryTimeout(self):
        return int(self.getConf(self.dnsQueryTimeout[0], self.dnsQueryTimeout[1]))

    def setPoisonType(self, value):
        self.setConf(self.poisonType[0], self.poisonType[1], str.encode(value))

    def getPoisonType(self):
        return self.getConf(self.poisonType[0], self.poisonType[1])

    def setReplaceIP(self, value):
        sel.fsetConf(self.replaceIP[0], self.replaceIP[1], str.encode(value))

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

    pass

