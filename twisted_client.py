#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.internet import reactor, protocol
from twisted.python import log
import time
import argparse


SIGNAL_PREFIX = "\x47\x87\x86"
ID = "test123"


def addr2str(addr):
    return "{0}:{1}".format(*addr)


def str2addr(addr):
    host, port = addr.split(":")
    return host, int(port)


def signal_msg(addr):
    return SIGNAL_PREFIX + ID + SIGNAL_PREFIX + addr2str(addr)


def read_signal_response(data):
    _, private_addr, public_addr = data.split(SIGNAL_PREFIX)
    return str2addr(private_addr), str2addr(public_addr)

log.startLogging(sys.stdout)


class UDPClient(protocol.DatagramProtocol):

    def __init__(self, signal_server):
        self.signal_server = signal_server
        self.connected = None
        self.private_addr = None
        self.public_addr = None

    def discover(self):
        if not self.connected:
            if self.private_addr and self.public_addr:
                log.msg("Send discover to: {} {}".format(
                        self.private_addr, self.public_addr))
                self.transport.write("discover", self.private_addr)
                self.transport.write("discover", self.public_addr)
            reactor.callLater(1, self.discover)

    def startProtocol(self):
        log.msg("Send request to signal server")
        addr = self.transport.getHost()
        self.transport.write(signal_msg((addr.host, addr.port)), self.signal_server)

    def datagramReceived(self, datagram, addr):
        if datagram.startswith(SIGNAL_PREFIX):
            log.msg("Received response from signal server")
            private_addr, public_addr = read_signal_response(datagram)
            self.public_addr = public_addr
            self.private_addr = private_addr
            self.discover()
            return
        elif datagram.startswith("discover"):
            if not self.connected:
                log.msg("Received discover message")
                self.connected = addr
                self.transport.connect(*addr)
                self.transport.write("discover")
                self.transport.write("hello i'm here")
        else:
            log.msg("Received message: {}".format(datagram))
            self.transport.write("hello i'm here")
            time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("signal_server", help="Public ip of signal server")
    args = parser.parse_args()
    host, port = args.signal_server.split(":")
    reactor.listenUDP(0, UDPClient((host, int(port))))
    reactor.run()
