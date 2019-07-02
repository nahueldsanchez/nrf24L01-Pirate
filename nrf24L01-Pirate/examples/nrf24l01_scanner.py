#!/usr/bin/env python2

'''
The following code is based on the nrf24-scanner.py
script from Bastille Networks.

https://github.com/BastilleResearch/nrf-research-firmware
'''

import argparse
import time
import sys
sys.path.append('../')
from nrf24l01 import *

parser = argparse.ArgumentParser()
parser.add_argument('--Device', help='Path to BusPirate Device', default='/dev/ttyUSB0')
parser.add_argument('--SCAN_CHANNELS', help='List of channels to scan', nargs='+', default=range(1,84), type=int)
parser.add_argument('--DWELL_TIME', help='Time to wait in each channel', default=0.5, type=int)
args = parser.parse_args()

nrf = nrf24L01(args.Device)
nrf.enter_promiscuous_mode()
nrf.channel = 0x01
nrf.print_details()
nrf.print_channel_and_freq()

SCAN_CHANNELS = args.SCAN_CHANNELS
DWELL_TIME = args.DWELL_TIME
last_tune = time.time()
channel_index = 0
second_pass = False

# From Bastille Networks nrf-research-firmware
def crc_update(crc, byte, bits):
    crc = crc ^ (byte << 8)
    for _ in range(bits):
        if((crc & 0x8000) == 0x8000):
            crc = (crc << 1) ^ 0x1021
        else:
            crc = crc << 1

        crc = crc & 0xFFFF
    return crc

def format_bytes(data):
    return ':'.join([format(x, '02x') for x in data]).upper()

while True:

    # Increment the channel
    if len(SCAN_CHANNELS) > 1 and time.time() - last_tune > DWELL_TIME:
        channel_index = (channel_index + 1) % (len(SCAN_CHANNELS))
        nrf.channel = (SCAN_CHANNELS[channel_index])
        last_tune = time.time()

# Receive payloads
    if nrf.is_data_available():

        raw_packet = list(nrf.read_data2())
        if len(raw_packet) >= 5:

            raw_packet = [ord(x) for x in raw_packet]

            #The following code is based on radio.c part of
            #the nrf-research-firmware from Bastille
            #networks.
            #https://github.com/BastilleResearch/nrf-research-firmware

            for _ in xrange(2):

                if second_pass:
                    for x in range(31,-1,-1):
                        if x > 0:
                            raw_packet[x] = raw_packet[x - 1] << 7 | raw_packet[x] >> 1
                        else:
                            raw_packet[x] = raw_packet[x] >> 1
                else:
                    second_pass = True

                payload_length = raw_packet[5] >> 2

                if payload_length <= 23:

                    crc_given = (raw_packet[6 + payload_length] << 9) | ((raw_packet[7 + payload_length]) << 1)
                    crc_given = (crc_given << 8) | (crc_given >> 8)
                    if(raw_packet[8 + payload_length] & 0x80):
                        crc_given |= 0x100

                    #Calculate the CRC
                    crc = 0xFFFF;

                    for x in range(6+payload_length):
                        crc = crc_update(crc, raw_packet[x], 8)

                    crc = crc_update(crc, raw_packet[6 + payload_length] & 0x80, 1)
                    crc = (crc << 8) | (crc >> 8)

                    if crc == crc_given:
                        print "Channel: %d Payload len: %d MAC: %s Payload: %s" % (nrf.channel, payload_length, format_bytes(raw_packet[:5]), format_bytes([(x << 1) for x in raw_packet[6:6+payload_length]]))

            second_pass = False


