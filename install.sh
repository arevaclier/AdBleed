#!/bin/bash
mv src/* .
rm -rf src/
echo Installing requirements...
sudo apt-get install nmap
pip3 install -r "requirements.txt"
chmod +x AdBleed
echo Done!
