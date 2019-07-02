import sys
import time
import string

sys.path.append('../')
from nrf24l01 import *

#Replace for your Bus pirate device
nrf = nrf24L01('/dev/ttyUSB0')

nrf.begin()
nrf.receive_address = 'RxAAA'
nrf.transmit_address = 'RxAAA'
nrf.set_data_rate(RF24_250KBPS)
nrf.enable_dynamic_payloads()
nrf.set_retries(15,15)
nrf.power_up()
nrf.print_details()

DATA = string.printable

while True:
    for counter in xrange(1,32):
        payload = DATA[:counter]
        print "Sending payload: %s" % payload

        if nrf.transmit_data(payload):
            print "Data successfully transmitted"

        else:
            print "Data transmission failed"

        time.sleep(1)