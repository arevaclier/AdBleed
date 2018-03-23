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
This will try to obtain the IP address of the Pi-hole in the network. It does this by querying all DNS servers in `/etc/resolv.conf` for known advertisment servers. AdBleed has a built-in list of ad servers, but also retrieves the latest versions of some of the ad lists used by Pi-hole by default. A few hosts are selected at random to test.

Since the Pi-hole returns its own IP address for every ad DNS request, AdBleed will check the answers of the DNS requests and select the Pi-hole IP if more than a certain percentage of the resulting IPs were equal.

### ARP Poisoning
To Do

### DNS Poisoning
DNS poisoning of the Pi-hole has several types. It can alter all responses or only the ad responses. Furthermore, the user can choose to replace the IP addresses in the DNS responses with a fixed IP address, its own IP address or a random IP address.

### Automate
Once set up, it is possible to set up AdBleed in automatic mode. This means it is started once the machine is booted and will automatically do the steps above according to the settings.

### Settings
AdBleed gives the user a range of settings to alter. The CLI offers an interface to change the settings, however it is also possible to change `AdBleed.conf`  by hand.

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
