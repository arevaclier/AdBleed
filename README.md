# AdBleed

## Description
AdBleed is an attack for a [Pi-hole](https://github.com/pi-hole/pi-hole). It can detect a Pi-hole on the network and automatically replace DNS requests sent back from the Pi-hole. This project uses Python 3 and [Scapy for Python 3](https://github.com/phaethon/scapy) to implement the network interaction.

AdBleed is intended to run on a Raspberry Pi (but will likely also work on other Linux machines). Together with the [automation](#automate), this makes a small device that can be plugged in independently to interfere with the Pi-hole.

## Table of Contents
- [Installation](#installation)  
- [Usage](#usage)
  - [Discovery](#discovery)
  - [ARP Poisoning](#arp-poisoning)
  - [DNS Poisoning](#dns-poisoning)
  - [Automate](#automate)
  - [Settings](#settings)
- [License](#license)

## Installation
To install, pull the repository from GitHub and run the installer:
```
git clone https://github.com/arevaclier/AdBleed.git
cd AdBleed
sudo ./install
```
AdBleed does not require the repository after the installer has been run. To update, `pull` the latest version and run `sudo ./install` again.

## Usage
To start the AdBleed CLI, run `sudo AdBleed`. AdBleed has several modes of operation.

### Discovery
This will try to obtain the IP address of the Pi-hole in the network. Depending on the setting in `AdBleed.conf`, it can use the DNS servers in `/etc/resolv.conf` or a custom range of IP addresses. If the user has selected a custom range of addresses, [nmap](https://pypi.python.org/pypi/python-nmap) will determine which hosts accept connections on port 53. In both case, all (open) addresses are queried for a number of known advertisment servers (this number can be set by the user). AdBleed has a built-in list of ad servers, but also retrieves the latest versions of some of the ad lists used by Pi-hole by default.

If a set percentage of responses is the IP address of the DNS server, AdBleed classifies the DNS server as possible Pi-hole. This mechanism is used because a Pi-hole will always return its own IP address if it is queried with a advertisement server. Finally the server with the most equal DNS responses is selected.

### ARP Poisoning
To Do

### DNS Poisoning
DNS poisoning of the Pi-hole has several types. It can alter all DNS responses or only the responses for requests of ad servers. Furthermore, the user can choose to replace the IP addresses in the DNS responses with a fixed IP address, its own IP address or a random IP address.

AdBleed sniffs all packets and acts on those with the previously determine IP address and source port 53. For these packets, the response IP address may be changed depending on the poisoning setting. All other packets are ignored.

### Automate
Once set up, it is possible to set up AdBleed in automatic mode. This means it is started once the machine is booted and will automatically do the steps above according to the settings.

### Settings
AdBleed gives the user a range of settings to alter. It is possible to change the settings in the file `AdBleed.conf`  by hand. This contains formatting examples and explanations on what the settings change.

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
