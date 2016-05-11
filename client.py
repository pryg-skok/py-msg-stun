#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import stun
import socket
import time

SIGNAL_PREFIX = "\x47\x87\x86"
ID = "test123"
#SIGNAL_SERVER_ADDR = ("127.0.0.1", 5000)
SIGNAL_SERVER_ADDR = ("188.234.152.66", 50142)
PORT = 5000


def addr2str(addr):
    return "{0}:{1}".format(*addr)

def str2addr(addr):
    host, port = addr.split(":")
    return host, int(port)


def request_conn(sock, addr):
    sock.sendto(SIGNAL_PREFIX + ID + SIGNAL_PREFIX + addr, SIGNAL_SERVER_ADDR)
    data, addr = sock.recvfrom(1024)
    _, private_addr, public_addr = data.split(SIGNAL_PREFIX)
    return str2addr(private_addr), str2addr(public_addr)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(10)
    nat_type, external_ip, external_port = stun.get_ip_info()
    other_client, other_client_nat = request_conn(s, addr2str((external_ip, external_port)))
    connected = None
    s.settimeout(2)
    while True:
        # discover procedure
        while not connected:
            for addr in [other_client, other_client_nat]:
                print("Try to conn to addr: {}".format(addr))
                s.sendto("discover", addr)
                try:
                    data, addr = s.recvfrom(1024)
                    s.sendto("discover", addr)
                except socket.timeout:
                    continue
                connected = addr
                print("Connected to: {}".format(addr))
        s.sendto("hello i'm here", connected)
        data, addr = s.recvfrom(1024)
        print("Received from {}: {}".format(addr, data))
        time.sleep(1)

if __name__ == "__main__":
    main()

