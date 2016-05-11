#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket


LISTEN_PORT = 5000
SIGNAL_PREFIX = "\x47\x87\x86"


def addr2str(addr):
    return "{0}:{1}".format(*addr)


def str2addr(addr):
    host, port = addr.split(":")
    return host, int(port)


def addr_msg(private_addr, public_addr):
    data = SIGNAL_PREFIX + addr2str(private_addr) + SIGNAL_PREFIX + addr2str(public_addr)
    return data


def main():
    wait_conn = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", LISTEN_PORT))
    print("Listen on {}".format(LISTEN_PORT))
    while True:
        data, private_addr = s.recvfrom(1024)
        # msg format: SIGNAL_PREFIX+unique_id
        _, uid, public_addr = data.split(SIGNAL_PREFIX)
        try:
            await_addr_private, await_addr_public = wait_conn.pop(uid)
        except:
            wait_conn[uid] = private_addr, str2addr(public_addr)
            print("register request: {} <-> {} ({})".format(
                  addr2str(private_addr), public_addr, uid))
            continue
        else:
            s.sendto(addr_msg(await_addr_private, await_addr_public), private_addr)
            s.sendto(addr_msg(private_addr, str2addr(public_addr)), await_addr_private)
            print("connected session: ({} {}) <-> ({} {})".format(
                  await_addr_private, await_addr_public, private_addr,
                  str2addr(public_addr)))

if __name__ == "__main__":
    main()
