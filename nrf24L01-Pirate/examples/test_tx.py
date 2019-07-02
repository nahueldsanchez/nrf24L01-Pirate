import sys
import time
sys.path.append('../')
from nrf24l01 import *

#Replace for your Bus pirate device
nrf = nrf24L01('/dev/ttyUSB0')

nrf.begin()
nrf.set_payload_size(1)
nrf.receive_address = 'RxAAA'
nrf.transmit_address = 'RxAAA'
nrf.set_data_rate(RF24_250KBPS)
nrf.power_up()
nrf.print_details()


counter = 0
while True:
    if nrf.transmit_data(str(counter)):
        print "Data successfully transmitted"
        counter += 1
    else:
        print "Data transmission failed"

    time.sleep(1)


