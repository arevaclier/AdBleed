import configparser

class Configuration:
    config
    path
    
    dnsQueryTimeout = ("Discovery", "DnsQueryTimeout")
    poisonType = ("Poisoning", "PoisonType")
    replaceIP = ("Poisoning", "ReplaceIP")

    def __init__():
        path = os.path.dirname(__file__) + "../AdBleed.conf"
        config = configparser.ConfigParser()
        config.read(path)
    
    def set(section, variable, value):
        config.set(section, variable, value)
        with open(path, "wb") as file:
            config.write(file)
            
    def get(section, variable):
        return config.get(section, variable)


    # --------------------
    # | Specific get/set |
    # --------------------
    def setDNSQueryTimeout(value):
        set(dnsQueryTimeout[0], dnsQueryTimeout[1], value)
    
    def getDNSQueryTimeout():
        return get(dnsQueryTimeout[0], dnsQueryTimeout[1])

    def setPoisonType(value):
        set(poisonType[0], poisonType[1], value)
    
    def getPoisonType():
        return get(poisonType[0], poisonType[1])
    
    def setReplaceIP(value):
        set(replaceIP[0], replaceIP[1], value)
    
    def getReplaceIP():
        return get(replaceIP[0], replaceIP[1])

    pass
