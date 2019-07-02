import sys
import time
sys.path.append('../')
from nrf24l01 import *

#Replace for your Bus pirate device
nrf = nrf24L01('/dev/ttyUSB0')

nrf.begin()
nrf.set_payload_size(10, 0)
nrf.receive_address = 'RxAAA'
nrf.transmit_address = 'RxAAA'
nrf.set_data_rate(RF24_2MBPS)
nrf.set_rx_mode()
nrf.print_config_register()
nrf.print_rfsetup_register()
nrf.print_status_register()
nrf.print_details()



while True:
    if nrf.is_data_available():
        print repr(nrf.read_data())
