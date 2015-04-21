#!/usr/bin/env bash

set -e
#set -v

# creates private key
#openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem <<EOF
MX
Mexico
Mexico
PulsarCloud
RDU
lenovo
fer.aguilar.reyes@gmail.com
EOF
# creates certificate file (public key) in DER
#openssl x509 -inform pem -in mycert.pem -outform der -out mycert.cer
openssl x509 -inform pem -in mycert.pem -outform der -out mycert.cer

# https://www.lisenet.com/2014/convert-p7b-to-pfx-with-openssl/
#openssl req -new -x509 -days 365 -sha256 -nodes -out cert.cer -keyout cert.key
#openssl pkcs12 -export -in cert.cer -inkey cert.key -out cert.pfx
