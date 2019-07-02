#!/usr/bin/env python2
'''
This code is based on the work performed by
Bastille Networks.

https://github.com/BastilleResearch/nrf-research-firmware/blob/02b84d1c4e59c0fb98263c83b2e7c7f9863a3b93/tools/nrf24-sniffer.py
'''

import argparse
import sys
import time
sys.path.append('../')
from nrf24l01 import *

parser = argparse.ArgumentParser()
parser.add_argument('--Device', help='Path to BusPirate Device', default='/dev/ttyUSB0')
parser.add_argument('--SCAN_CHANNELS', help='List of channels to scan', nargs='+', default=range(1,84), type=int)
parser.add_argument('MAC', help='MAC to sniff, example: 12:A7:98:4F:BF, LSB goes first!')

args = parser.parse_args()

nrf = nrf24L01(args.Device)
nrf.begin()
nrf.power_down()

nrf.receive_address = ''.join([x.decode('hex') for x in args.MAC.split(':')])
nrf.transmit_address = ''.join([x.decode('hex') for x in args.MAC.split(':')])

nrf.set_data_rate(RF24_2MBPS)
nrf.enable_dynamic_payloads()
nrf.set_retries(15,15)
nrf.channel = 0x01
nrf.power_up()
nrf.print_details()
last_ping = time.time()
channel_found = False
timeout = 0.4

def send_ping():
    for attempt in xrange(1, 4):
        if nrf.transmit_data('AAAA'):
            return True

    return False

while True:
    if time.time() - last_ping > timeout:
        nrf.enable_dynamic_payloads()
        nrf.set_retries(15,15)

        if not send_ping():
            for channel in args.SCAN_CHANNELS:
                nrf.channel = channel
                print 'Setting channel: %d' % channel
                if send_ping():
                    print 'got ACK on channel: %d' % (nrf.channel)
                    last_ping = time.time()
                    channel_found = True
                    break
            if not channel_found:
                print 'Cant find address: %s' % repr(nrf.receive_address)
        else:
            print 'Address found on channel: %d' % nrf.channel
            last_ping = time.time()
    else:

        nrf.auto_ack = 0
        nrf.set_rx_mode()
        if nrf.is_data_available():
            last_ping = time.time()
            value = nrf.read_data()
            value_pp = [str.format('{:02X}', ord(x)) for x in value]
            value_pp = ':'.join(value_pp)
            print value_pp