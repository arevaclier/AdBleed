#!/bin/bash
mv src/* .
rm -rf src/
echo Installing requirements...
pip install -r "requirements.txt"
chmod +x AdBleed
echo Done!
