#!/usr/bin/env python

# Generate mac addresses in the range
# 00:50:56:00:00:00 - 00:50:56:3F:FF:FF

import random

def random_mac():
    """
    from xend/server/netif.py
    Generate a random MAC address.
    Uses OUI 00-50-56, allocated to
    VMWare. Last 3 fields are random.
    return: MAC address string
    """
    mac = [ 0x00, 0x50, 0x56,
        random.randint(0x00, 0x3f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

def mac_range():
    """
    Generate a list of all the macs
    """
    mac_list = []
    for a in range(0x00, 0x3f):
        for b in range(0x00, 0xff):
            for c in range(0x00, 0xff):
                mac_list.append("00:50:56:%0.2x:%0.2x:%0.2x" % (a,b,c))

print random_mac()
