###### Note: this branch is to be used with the provided installer. It does not contain the automated attack
# AdBleed
 
## Description
AdBleed is an attack for a [Pi-hole](https://github.com/pi-hole/pi-hole). It can detect a Pi-hole on the network and automatically replace DNS requests sent back from the Pi-hole. This project uses Python 3, [Scapy for Python 3](https://github.com/phaethon/scapy) and [python-nmap](https://pypi.python.org/pypi/python-nmap) to implement the network interaction.
 
AdBleed is designed to run on a Raspberry Pi (but will likely also work on other Linux machines). 
The only requirements for AdBleed are a working instance of Python 3 and [pip](https://pypi.python.org/pypi/pip/). Other needed packages are installed by the installer.
 
### Attack reproduction
To reproduce this attack, the following equipment is required:
- A Raspberry Pi running Pi-hole and configured as the default DNS server on the network.
- A Raspberry Pi (or a linux machine) running this script.
- A third host (any computer, …) to generate DNS traffic.
 
Once the network is up and configured with the Pi-hole as the primary DNS server, the attacker just needs to launch the attack to replace either all domains returned by the Pi-hole or only the blocked ads. Once the third hosts requests a either a domain or a blocked ad, the attacker will see the IP that was set replacing the IP returned by the Pi-hole
 
### Motivations behind the attack
The goal of the Pi-hole is to sinkhole a number of ads and domains such that hosts on the network are exempt from potentially dangerous websites and ads.
If an attacker can recognize the blocked ads and is able to redirect this traffic to his own ad server in a seamless way, there is potential for financial gain.
 
## Table of Contents
- [Installation](#installation)  
- [Attack Description](#attack-description)
- [Usage](#usage)
  - [Discovery](#discovery)
  - [ARP Poisoning](#arp-poisoning)
  - [DNS Poisoning](#dns-poisoning)
  - [Settings](#settings)
- [License](#license)
 
## Installation
To install, pull the repository from GitHub and run the installer:
```
git clone https://github.com/arevaclier/AdBleed.git
cd AdBleed
sudo ./install.sh
```
To update, `pull` the latest version and run `sudo ./install.sh` again.
 
## Attack Description
This tool performs its attack in three stages. The **discovery** system will search a part of the network. The user can specify if this should be a range of IP addresses or the addresses found in `/etc/resolv.conf`. For the former, nmap performs a port scan to determine possible DNS servers. With the resulting list, several DNS requests are made.  
Because the Pi-hole will return its own IP, AdBleed can determine if a DNS server is a Pi-hole. Namely, if a high percentage of responses contains the same IP address, it expects the server to be a Pi-hole. One address will be selected to perform the attack on.
 
The second stage is **ARP poisoning**. The goal is to make the Pi-hole believe that all hosts (IPs) are located at the attacker’s MAC address. This will make the Pi-hole return every request to the attacker such that they can change these responses. The ARP caches of other systems in the network do not need poisoning since we just need the responses from the Pi-hole. Other systems should indeed work normally. 
If the cache of the Pi-hole is poisoned, a thread is started to keep this poisoning. Without it, other hosts would restore the ARP cache with their legitimate broadcasts. By default, the thread repeats the attack every five seconds.
Moreover, since devices can connect and disconnect from the network, the attack refreshes the list of alive hosts every once in a while (by default, every 100 iterations).
 
Once cache of the Pi-hole is poisoned, the user can start the core attack, **DNS poisoning**. Various settings can be used to alter the exact behaviour of this attack for this, see the part on [DNS poisoning in usage](#dns-poisoning). In any case, the attacker will receive all responses created by the Pi-hole due to the ARP poisoning. Depending on the settings, the attacker will have the opportunity to change IP addresses in the responses.  
This might be used to direct all ads to a server hosted by attacker, or cause chaos by changing all DNS requests. This attack will only affect hosts that are using the Pi-hole as their DNS server.
 
## Usage
To start the AdBleed CLI, run `sudo ./AdBleed`. AdBleed has several modes of operation.
 
### Discovery
By selecting option 1 in the main AdBleed menu, the discovery process is started. Next, the user is prompted with the settings from `AdBleed.conf` and can accept or reject to start the discovery process. The user has control of the following settings to customize the discovery:
```
[Discovery]
# Maximum time to wait to receive DNS response for discovery, in ms.
DnsQueryTimeout = 100
# Minimum percentage of hosts to result in the same IP to classify DNS server as Pi-hole
SimilarResp = 75
# Number of hosts to randomly test at the DNS server
NumberOfHosts = 50
# Search for the Pi-hole in a range of IP addresses or in /etc/resolv.conf
;DNSServer = 'resolv.conf'
DNSServer = '192.168.0.0/24'
 
HostsURL = ‘’
```
Firstly, `DNSServer` lists which hosts to possibly classify as DNS server (this must include the Pi-hole). If set to `resolv.conf` the contents of this file are used to query. Port scanning is skipped for these hosts. Alternatively, a (range of) IP addresses can be given to scan for Pi-holes.
 
Next, `DnsQueryTimeout` is used to limit the time we wait for a DNS response from a DNS server. This is to prevent extremely long discovery times. Our testing showed that local DNS servers should generally produce a result well within 100 ms. The user can change this if discovery takes too long or if a Pi-hole takes too long to respond.
 
`NumberOfHosts` is the number of queries made to each possible DNS server. Higher numbers are likely to return more accurate Pi-holes. However, more requests takes longer. At most DnsQueryTimeout per added host.
 
`SimilarResp` gives the minimum percentage of requests that had the IP as response. If no DNS server exceeds this threshold, AdBleed reports that no Pi-hole was found. If multiple servers exceed this threshold, the highest percentage is automatically selected.
 
Finally, `HostsURL` is there to provide the user a way to add its own list of hosts that can be used to find a Pi-hole on the network. Since the lists can change, it is necessary to provide an easy way to add hosts in case the integrated lists becomes deprecated.
The list needs to follow a strict format:
- Commented lines need to start with a “#”
- The domains are listed either as “0.0.0.0 domain.com” or “domain.com”
- There is only one domain per line
- The URL must lead to raw text.
[This](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts) is an example of such a list.
 
### ARP Poisoning
ARP poisoning can run in several different ways, and we chose to implement the attack over layer 2. Some settings are available to customize it:
```
[General]
# Network interface used to carry out the attacks
NetworkInterface = enp5s0
 
...
 
[Poisoning]
...
# Define ARP poisoning targets.
# If set to none, ARP poisoning will take place on every host in the same subnet as the DNS server
ARPtarget = ''
;ARPtarget = '192.168.0.1/24'  # Force targets for ARP poisoning
 
# Time between ARP packets (in seconds)
ARPdelay = 5
 
# Number of arp attacks before refreshing list of alive hosts
ARPrefreshDelay = 100
```
In order, `NetworkInterface` defines which network interface AdBleed is going to use to carry out ARP poisoning. It is possible to get the name of your interfaces by running the `ifconfig` command in a terminal.
 
`ARPTarget` defines the range of IPs ARP poisoning is going to affect. If left blank, it will use the same range as the parameter `DNSServer` in section `[Discovery]`. Examples of possible values are `192.168.0.1/24`, `10.0.0.1/16`, etc.
 
`ARPdelay` defines the elapsed time between two ARP poisoning attacks (in seconds). Since the ARP cache is regularly updated on most systems, it is necessary to carry out the attack repeatedly.
 
`ARPrefreshDelay` defines how often the list of alive hosts is refreshed (in number of attacks). By default, the list is updated each 100 attacks.
 
### DNS Poisoning
The last attack stage also has some settings. These setting will need to be changed to adapt this tool for the attackers purpose.
```
[Poisoning]
# Type of DNS poisoning to execute
PoisonType = ads
;PoisonType = complete          # Replace every DNS request
 
...
 
# Which IP should be substituted
ReplaceIP = 1.1.1.1
;ReplaceIP = random
;ReplaceIP = own
 
# Number of seconds to change DNS responses, =0 for infinitely
SpoofingTimeout = 3600
```
The `PoisonType` can be `ads` or `complete`. Ads will only change responses that the Pi-hole classified as advertisement servers (i.e. all responses that have the previously determined IP of the Pi-hole). In the case of complete, all requests are changed. This is feature is intended to cause chaos.
 
`ReplaceIP` has three possible values. A certain IP address will change the responses selected by the previous setting with a static IP address. `random` will generate a completely random address. This will reduce the likelihood that the attacker can be found. Finally, `own` is intended to have the attacker run their own ad server to show ads where the Pi-hole tries to block those.
 
Lastly, `SpoofingTimeout` is a time in seconds after which the DNS spoofing is aborted. If the attacker wishes not to use this, it can be set to 0 for infinite spoofing.
 
## License
**MIT License**
 
Copyright (c) 2018 AdBleed
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


