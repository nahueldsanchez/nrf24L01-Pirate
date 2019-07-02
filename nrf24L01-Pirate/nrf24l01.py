# This library is based on the work done by the following people: 
# Kevin Mehall <km@kevinmehall.net> https://github.com/kevinmehall/nRF24L01-buspirate
# Samy Kamkar https://github.com/samyk/keysweeper
# Travis Goodspeed https://travisgoodspeed.blogspot.com/2011/02/promiscuity-is-nrf24l01s-duty.html
# Bastille Research https://github.com/BastilleResearch/nrf-research-firmware/

import serial
import time
import sys

class BP_SPI(object):
    """BusPirate SPI library"""
    def __init__(self, port):
        self.serial = serial.Serial(port, 115200, timeout=0.1)
        self.serial.write('\x00\x0f')
        self.serial.flush()
        time.sleep(0.1)
        self.serial.write('\r\n'*10 + '#')
        time.sleep(0.1)
        self.serial.write('\0'*20 + chr(0x01))
        self.serial.flush()
        time.sleep(0.1)
        
        i = self.serial.read(self.serial.inWaiting())
        if not i.endswith("SPI1"):
            raise IOError("Could not initialize BusPirate")
            
        self._power = True
        self._pullup = False
        self._aux = False
        self._cs = True
    
    def setCS(self, val):
        self.serial.write(chr(0x02 | bool(val)))
        assert(self.serial.read(1) == chr(1))
        self._cs = val
        
    def transfer(self, data='', size=0):
        """Read /size/ bytes while writing /data/"""
        size = max(len(data), size)
        data += (size - len(data)) * '\0'
        buff = chr(0x10|(size-1))+data
        self.serial.write(buff)
        self.serial.flush()
        d = self.serial.read(size+1)
        assert(d[0] == chr(1))
        return d[1:]
        
    def cs_transfer(self, data='', size=0):
        """Pull CS low, perform a transfer, and then raise CS, minimizing serial delays"""
        size = max(len(data), size)
        data += (size - len(data)) * '\0'
        self.serial.write(chr(0x02)+chr(0x10|(size-1))+data+chr(0x03))
        self.serial.flush()
        d = self.serial.read(size+3)
        assert (d[0] == chr(1) and d[1] == chr(1) and d[-1] == chr(1))
        return d[2:-1]
        
    def set_outputs(self, power=None, pullup=None, aux=None, cs=None):
        if power is None:  power = self._power
        if pullup is None: pullup = self._pullup
        if aux is None:    aux = self._aux
        if cs is None:     cs = self._cs 
        self.serial.write(chr(0x40
              | (bool(power) << 3)
              | (bool(pullup) << 2)
              | (bool(aux) << 1)
              | bool(cs)))
        assert(self.serial.read(1) == chr(1))
        self._power, self._pullup, self._aux, self._cs = power, pullup, aux, cs
        
    def set_mode(self, power, ckp, cke, smp):
        self.serial.write(chr(0x80
              | (bool(power) << 3)
              | (bool(ckp) << 2)
              | (bool(cke) << 1)
              | bool(smp)))
        assert(self.serial.read(1) == chr(1))

# Registers
CONFIG = 0x00
EN_AA = 0x01
EN_RXADDR = 0x02
SETUP_AW = 0x03
SETUP_RETR = 0x04
RF_CH = 0x05
RF_SETUP = 0x06
STATUS = 0x07
OBSERVE_TX = 0x08
CD = 0x09
RX_ADDR_P0 = 0x0A
RX_ADDR_P1 = 0x0B
RX_ADDR_P2 = 0x0C
RX_ADDR_P3 = 0x0D
RX_ADDR_P4 = 0x0E
RX_ADDR_P5 = 0x0F
TX_ADDR = 0x10
RX_PW_P0 = 0x11
RX_PW_P1 = 0x12
RX_PW_P2 = 0x13
RX_PW_P3 = 0x14
RX_PW_P4 = 0x15
RX_PW_P5 = 0x16
FIFO_STATUS = 0x17
DYNPD = 0x1C
FEATURE = 0x1D

# Bit Mnemonics
MASK_RX_DR = 6
MASK_TX_DS = 5
MASK_MAX_RT = 4
EN_CRC = 3
CRCO = 2
PWR_UP = 1
PRIM_RX = 0
ENAA_P5 = 5
ENAA_P4 = 4
ENAA_P3 = 3
ENAA_P2 = 2
ENAA_P1 = 1
ENAA_P0 = 0
ERX_P5 = 5
ERX_P4 = 4
ERX_P3 = 3
ERX_P2 = 2
ERX_P1 = 1
ERX_P0 = 0
AW = 0
ARD = 4
ARC = 0
PLL_LOCK = 4
RF_DR = 3
RF_PWR = 1
LNA_HCURR = 0
RX_DR = 6
TX_DS = 5
MAX_RT = 4
RX_P_NO = 1
TX_FULL = 0
PLOS_CNT = 4
ARC_CNT = 0
TX_REUSE = 6
FIFO_FULL = 5
TX_EMPTY = 4
RX_FULL = 1
RX_EMPTY = 0

# Instruction Mnemonics 
R_REGISTER = 0x00
W_REGISTER = 0x20
REGISTER_MASK = 0x1F
R_RX_PAYLOAD = 0x61
W_TX_PAYLOAD = 0xA0
R_RX_PL_WID = 0x60
FLUSH_TX = 0xE1
FLUSH_RX = 0xE2
REUSE_TX_PL = 0xE3
NOP = 0xFF

#Data rates
RF24_1MBPS = 0
RF24_2MBPS = 1
RF24_250KBPS = 2

#Feature bits
EN_DPL = 2
EN_ACK_PAY = 1
EN_DYN_ACK = 0


class nrf24L01(BP_SPI):
    #csn = cs, ce = AUX
    def __init__(self, port):
        super(nrf24L01, self).__init__(port)
        self.set_mode(power=1, ckp=0, cke=1, smp=0)
        self.set_outputs(cs=True, aux=False, power=True)
        
    def configRegister(self, reg, value):
        """Write a byte to a configuration register"""
        self.cs_transfer(chr(W_REGISTER | (REGISTER_MASK & reg)) + chr(value))

    def readRegister(self, reg, size=1):
        """Read a configuration register"""
        return self.cs_transfer(chr(R_REGISTER | (REGISTER_MASK & reg)), size=size+1)[1:]
    
    def writeRegister(self, reg, data):
        """Write one or more bytes to a configuration register"""
        self.cs_transfer(chr(W_REGISTER | (REGISTER_MASK & reg))+data)

    def _get_register_bits(self, reg):
        """Returns bits for a given register in a string. s[0] is LSB"""
        value = ord(self.readRegister(reg))
        config_reg_value = format(value, '08b')[::-1]

        return config_reg_value

    def print_config_register(self):

        bits = self._get_register_bits(CONFIG)
        print "\n==Configuration Register values==\n"
        #print 'MASK_RX_DR: %s'  % bits[6]
        #print 'MASK_TX_DS: %s'  % bits[5]
        #print 'MASK_MAX_RT: %s' % bits[4]

        #Enable CRC. Forced high if one of the bits in the
        #EN_AA is high
        print 'CRC Enabled: %s' % bits[3]
        
        #CRC encoding scheme
        #'0' - 1 byte
        #'1' - 2 bytes
        crc_enc = {'0': '1 byte', '1': '2 bytes'}
        print 'CRC Encoding scheme: %s' % crc_enc[bits[CRCO]]

        #PWR_UP
        pwr_up = {'1': 'POWER UP', '0':'POWER DOWN'}
        print 'Power control: %s' % pwr_up[bits[PWR_UP]]

        #PRIM_RX RX/TX control
        prim_rx = {'0': 'PTX',
                   '1': 'PRX'}
        print 'RX/TX: %s'     % prim_rx[bits[PRIM_RX]]

    def print_rfsetup_register(self):

        bits = self._get_register_bits(RF_SETUP)

        print "\n==RF_SETUP Register values==\n"
        print 'CONT_WAVE: %s' % bits[7]
        #PLL_LOCK (only used in testing)
        
        #RF_DR_LOW
        #RF_DR_HIGH
        #Select between the high speed data rates. This bit
        #is don't care if RF_DR_LOW is set.
        #Encoding:
        #[RF_DR_LOW, RF_DR_HIGH]:
        #'00' - 1Mbps
        #'01' - 2Mbps
        #'10' - 250kbps
        #'11' - Reserved
        data_rates = {'00':'1Mbps',
                      '01':'2Mbps',
                      '10':'250Kbps',
                      '11':'Reserved'}

        print 'Data rate: %s' % data_rates[bits[5]+bits[3]]

        #RF_PWR
        #Set RF output power in TX mode
        # '00' - -18dBm
        # '01' - -12dBm
        # '10' - -6dBm
        # '11' - 0dBm
        power_values = {'00':'-18dBm',
                        '01':'-12dBm',
                        '10':'-6dBm',
                        '11':'0dBm'}

        print 'Output Power: %s' % power_values[bits[1:3]]

    def print_status_register(self):
    
        bits = self._get_register_bits(STATUS)

        print "\n==STATUS Register values==\n"
        
        print 'Data Ready RX FIFO interrupt (RX_DR): %s' % bits[6]
        print 'Data Sent TX FIFO interrupt (TX_DS): %s' % bits[5]
        print 'Maximum number of TX (MAX_RT): %s' % bits[4]

        rx_p_no_options = {'111':'RX FIFO Empty',
                           '110':'Not used'}
        reg_val = bits[1:4]

        if reg_val in rx_p_no_options.keys():
            print 'Data pipe number for reading (RX_P_NO): %s' % rx_p_no_options[reg_val]
        else:
            print 'Data pipe number for reading (RX_P_NO): %d' % int(reg_val, 2)
        
        print 'TX FIFO full flag: %s' % bits[0]

    def set_rx_mode(self):

        config_reg = list(self._get_register_bits(CONFIG))
        config_reg[PWR_UP] = '1'
        config_reg[PRIM_RX] = '1'
        self.configRegister(CONFIG, int(''.join(config_reg)[::-1], 2))
        self.set_outputs(aux=True, cs=True) # CE = 1 (High)

        #print "RX Mode Entered"

    def set_tx_mode(self):
        config_reg = list(self._get_register_bits(CONFIG))
        config_reg[PWR_UP] = '1'
        config_reg[PRIM_RX] = '0'
        self.configRegister(CONFIG, int(''.join(config_reg)[::-1], 2))
        self.set_outputs(aux=True, cs=True) # CE = 1 (High)

    def is_data_available(self):

        fifo_status_bits = self._get_register_bits(FIFO_STATUS)

        return not bool(int(fifo_status_bits[RX_EMPTY]))


    def get_payload_size(self, data_pipe_number=0):

        assert 0<= data_pipe_number < 6
        #RX_PW_P0 is register 0x11, we add 0x11 to the pipe number
        #and obtain the correct register
        
        return ord(self.readRegister(data_pipe_number + 0x11))


    def set_payload_size(self, payload_len, data_pipe_number=0):
        
        assert 0<= data_pipe_number < 6
        assert payload_len <= 32
        #RX_PW_P0 is register 0x11, we add 0x11 to the pipe number
        #and obtain the correct register

        self.configRegister(data_pipe_number + RX_PW_P0, payload_len)

    def clear_rx_dr_bit(self):
        status_bits = list(self._get_register_bits(STATUS))
        
        status_bits[RX_DR] = '1'
        #Data Ready RX FIFO interrupt. Asserted when
        #new data arrives RX FIFO c .
        #Write 1 to clear bit.
        self.configRegister(STATUS, int(''.join(status_bits)[::-1],2))
    
    def clear_tx_ds_bit(self):
        status_bits = list(self._get_register_bits(STATUS))
        status_bits[TX_DS] = '1'
        self.configRegister(STATUS, int(''.join(status_bits)[::-1],2))

    def read_data(self):

        buff = []
        if self.dynamic_payloads_enabled():
            payload_size = self.get_dynamic_payload_size()
        else:
            payload_size = self.get_payload_size()

        # ToDo:
        # It's possible to implement this in an
        # (much) better and faster way as it
        # should be possible to read UP TO 16
        # bytes at once, but so far I could make
        # it work.
        # Reference: http://dangerousprototypes.com/docs/SPI_(binary)#0001xxxx_-_Bulk_SPI_transfer.2C_send.2Fread_1-16_bytes_.280.3D1byte.21.29

        self.setCS(False)
        buff.append(self.transfer(chr(R_RX_PAYLOAD)))

        for _ in xrange(payload_size):
            buff.append(self.transfer('\x00'))

        self.setCS(True)

        self.flush_rx()
        self.clear_rx_dr_bit()

        return ''.join(buff[1:])

    def read_data2(self):
        buff = []

        self.setCS(False)
        buff.append(self.transfer(chr(R_RX_PAYLOAD)))
        buff.append(self.transfer('\x00' * 16))
        buff.append(self.transfer('\x00' * 16))

        self.setCS(True)

        self.flush_rx()
        self.clear_rx_dr_bit()

        return ''.join(buff[1:])

    def transmit_data(self, payload):

        status_bits = self._get_register_bits(STATUS)

        #Todo: Check OBSERVE_TX register

        if not self.dynamic_payloads_enabled():
            payload = payload.ljust(self.get_payload_size(),'\x00')

        payload_len = len(payload)

        self.setCS(False)
        self.transfer(chr(W_TX_PAYLOAD))

        #ToDo: Do this in an better way
        if payload_len < 16:
            self.transfer(payload)
        else:
            for x in xrange(payload_len):
                self.transfer(payload[x])
        #################################

        self.setCS(True)

        #After calling this function if there is packet in the TX FIFO
        #It will be sent.
        self.set_tx_mode()

        #Let's check the status for the previous sending task
        status_bits = self._get_register_bits(STATUS)
        status_bits = list(status_bits)

        #If the packet was received and ACKnowledged the TX_DS
        #Will be set (if Auto ACK is enabled)
        if self.auto_ack_enabled:
            if status_bits[TX_DS] == '1':
                # The Packet was successfully transmitted
                # It could be possible that the ACK has a payload
                # to check this we've the RX_DR flag

                ####################################################
                #Todo: Move this outside this function
                #Or return this information
                if status_bits[RX_DR] == '1':
                    #The ACK has a payload
                    ack_payload_data = self.read_data()
                    print "ACK Payload data: %s" % ack_payload_data
                ####################################################

                #We clear the TX_DS bit (AS the documentation states, to clear
                #this bit we've to write an 1 into it).
                status_bits[TX_DS] = '1'
                self.configRegister(STATUS, int(''.join(status_bits)[::-1], 2))
                status_bits = self._get_register_bits(STATUS)

                return True
            else:
                if status_bits[MAX_RT] == '1':
                    #We reached the max amount of TX attempts
                    #We reset the MAX_RT flag and flush the TX FIFO
                    self.flush_tx()
                    status_bits[MAX_RT] = '1'
                    self.configRegister(STATUS, int(''.join(status_bits)[::-1], 2))
                    return False
        else:
            return True

    def set_retries(self, delay, count):
        assert 0 <= delay <= 15
        assert 0 <= count <= 15
        us_delay = 250 + (delay * 250)
        #ARD[7:4]
        #ARC[3:0]
        reg = format(delay, '04b') + format(count, '04b')
        self.configRegister(SETUP_RETR, int(reg, 2))

    def begin(self):
        #AUX = CE
        self.set_outputs(power=True, aux=False, cs=True)
        self.configRegister(CONFIG, 0x0C)                   #Reset NRF_CONFIG and enable 16-bit CRC.
        self.set_retries(5,15)                              #Set 1500uS (minimum for 32B payload in ESB@250KBPS)
                                                            #timeouts, to make testing a little easier
        self.configRegister(RF_SETUP, int('00001110', 2))   #2Mbps, 0dBm
        self.configRegister(FEATURE, 0)
        self.configRegister(DYNPD, 0)
        self.channel = 76
        self.clear_rx_dr_bit()

    def power_up(self):
        cfg_bits = list(self._get_register_bits(CONFIG))

        if cfg_bits[PWR_UP] != '1':
            cfg_bits[PWR_UP] = '1'
            self.configRegister(CONFIG, int(''.join(cfg_bits)[::-1],2))
    
    def set_data_rate(self, rate):

        assert 0 <= rate <= 2
        rf_bits = list(self._get_register_bits(RF_SETUP))
        #RF_SETUP
        #RF_DR_HIGH[3]
        #RF_DR_LOW[5]
        rate_bits = format(rate, '02b')

        rf_bits[5] = rate_bits[0]
        rf_bits[3] = rate_bits[1]

        self.configRegister(RF_SETUP, int(''.join(rf_bits[::-1]), 2))

    def flush_rx(self):
        self.setCS(False)
        self.transfer(chr(FLUSH_RX))
        self.setCS(True)

    def flush_tx(self):
        self.setCS(False)
        self.transfer(chr(FLUSH_TX))
        self.setCS(True)

    def power_down(self):
        self.set_outputs(aux=False)
        reg_bits = list(self._get_register_bits(CONFIG))
        reg_bits[PWR_UP] = '0'
        self.configRegister(CONFIG, int(''.join(reg_bits)[::-1], 2))

    def get_dynamic_payload_size(self):
        size = []
        """returns the size of the dynamic payload"""
        self.setCS(False)
        self.transfer(chr(R_RX_PL_WID), 1)
        size = self.transfer(chr(0xFF), 1)
        self.setCS(True)

        return ord(size)

    def enable_dynamic_payloads(self):
        feature_bits = list(self._get_register_bits(FEATURE))
        feature_bits[EN_DPL] = '1'
        self.configRegister(FEATURE, int(''.join(feature_bits)[::-1], 2))
        self.configRegister(DYNPD, int('00111111', 2))

    def dynamic_payloads_enabled(self):
        feature_bits = list(self._get_register_bits(FEATURE))

        return bool(int(feature_bits[EN_DPL]))

    def disable_dynamic_payloads(self):
        feature_bits = list(self._get_register_bits(FEATURE))
        feature_bits[EN_DPL] = '0'
        self.configRegister(FEATURE, int(''.join(feature_bits)[::-1], 2))

    def enable_CRC(self):
        config_bits = list(self._get_register_bits(CONFIG))
        config_bits[EN_CRC] = '1'
        self.configRegister(CONFIG, int(''.join(config_bits)[::-1], 2))

    def CRC_enabled(self):
        config_bits = list(self._get_register_bits(CONFIG))

        return bool(int(config_bits[EN_CRC]))

    def disable_CRC(self):
        config_bits = list(self._get_register_bits(CONFIG))
        config_bits[EN_CRC] = '0'
        self.configRegister(CONFIG, int(''.join(config_bits)[::-1], 2))
    
    def enter_promiscuous_mode(self, addr=''):
        self.begin()
        self.enable_rx_addresses(1)     #Enable ERX_P0
        self.address_width = 2

        #Looks like the order of the following commands it's
        #important.
        #This code is based on Travis goodspeed ideas/Research
        #and also Sammy Kamkar
        #You can find more references here:
        #https://travisgoodspeed.blogspot.com/2011/02/promiscuity-is-nrf24l01s-duty.html
        #https://github.com/samyk/keysweeper

        if addr:
            self.address_width = len(addr)
            self.receive_address = addr
        else:
            self.receive_address = '\xAA\x00'

        self.disable_dynamic_payloads()
        self.auto_ack = 0
        self.disable_CRC()
        self.set_data_rate(RF24_2MBPS)
        self.set_payload_size(32, 0)
        self.power_up()
        self.set_rx_mode()


    def print_details(self):

        status_bits = self._get_register_bits(STATUS)

        print "\n\n DEBUGGING INFORMATION \n\n"
        print "STATUS       = %s RX_DR=%s TX_DS=%s MAX_RT=%s RX_P_NO=%s TX_FULL=%s" % (hex(int(''.join(status_bits[::-1]),2)), status_bits[6],
                                                                                       status_bits[5], status_bits[4], 
                                                                                       int(''.join(status_bits[1:4]),2), status_bits[0])

        print "RX_ADDR_P0-1 = %s" % (self.receive_address)
        print "RX_ADDR_P2-5 = %s" % ("TODO")
        print "TX_ADDR      = %s" % (self.transmit_address)
        print "RX_PW_P0     = %s" % hex(ord(self.readRegister(RX_PW_P0)))
        print "EN_AA        = %s" % hex(ord(self.readRegister(EN_AA)))
        print "EN_RXADDR    = %s" % hex(ord(self.readRegister(EN_RXADDR)))
        print "RF_CH        = %s" % hex(ord(self.readRegister(RF_CH)))
        print "RF_SETUP     = %s" % hex(ord(self.readRegister(RF_SETUP)))
        print "CONFIG       = %s" % hex(ord(self.readRegister(CONFIG)))
        print "DYNPD/FEATURE= %s %s" % (hex(ord(self.readRegister(DYNPD))), hex(ord(self.readRegister(FEATURE))))
        #print "Data Rate    = %s" % 

    def test_carrier(self):

        return (ord(self.readRegister(CD)) & 1)

    @property
    def receive_address(self):
        """Returns the configured receive address, taking in to account the configured address_width"""
        addr_len = int(self._get_register_bits(SETUP_AW)[:2], 2) + 2

        return self.readRegister(RX_ADDR_P0, addr_len)

    @receive_address.setter
    def receive_address(self, receive_address):
        """Sets the receive address register"""
        self.writeRegister(RX_ADDR_P0, receive_address)

    @property
    def transmit_address(self):

        return self.readRegister(TX_ADDR, 5)

    @transmit_address.setter
    def transmit_address(self, transmit_address):

        return self.writeRegister(TX_ADDR, transmit_address)

    @property
    def address_width(self):
        """returns the configured address with in Bytes"""
        addr_width_values = {'00':'2 Bytes (Illegal)',
                            '01':'3 Bytes',
                            '10':'4 Bytes',
                            '11':'5 Bytes'}

        print addr_width_values[self._get_register_bits(SETUP_AW)[:2]]

        return int(self._get_register_bits(SETUP_AW)[:2], 2) + 2

    @address_width.setter
    def address_width(self, value):
        self.configRegister(SETUP_AW, value-2)

    def auto_ack_enabled(self, datapipe=0):
        assert 0 <= datapipe <= 5
        en_aa_bit = self._get_register_bits(EN_AA)[datapipe]

        if en_aa_bit == '0':
            return False

        return True

    @property
    def auto_ack(self):
        en_aa_bits = self._get_register_bits(EN_AA)[:6]

        for index, _ in enumerate(en_aa_bits):
            print 'ENAA_P%d: %s' % (index, bool(int(en_aa_bits[index])))

        return en_aa_bits

    @auto_ack.setter
    def auto_ack(self, value):
        self.configRegister(EN_AA, value)

    def enable_rx_addresses(self, value):
        self.configRegister(EN_RXADDR, value)

    @property
    def channel(self):

        channel_number = ord(self.readRegister(RF_CH))
        return channel_number

    def print_channel_and_freq(self):
        print 'Channel number: %d, freq: %d MHz' % (self.channel, 2400 + self.channel)

    @channel.setter
    def channel(self, value):
        assert value < 126
        self.configRegister(RF_CH, value)

