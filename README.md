# py-msg-stun

signal_server.py - randevouz server and actually it works as STUN server here, but without
type of NAT detection

twisted_client.py - simple script to show the concept of p2p messaging based on Twisted

# How to run

run signal_server.py

run twisted_client on machine A and on machine B

signal_server.py connects two clients between each other and they start messaging - both
behind NAT

