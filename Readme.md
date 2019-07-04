# Python nrf24L01-Pirate library

## Disclaimer

A lot of this project it's based on the work of other people:

* Kevin Mehall - [nRF24L01-buspirate](https://github.com/kevinmehall/nRF24L01-buspirate)
* Samy Kamkar - [KeySweeper] (https://github.com/samyk/keysweeper)
* Travis Goodspeed - [Original research to enable sniffing for the NRF24L01](https://travisgoodspeed.blogspot.com/2011/02/promiscuity-is-nrf24l01s-duty.html)
* Marcus Mengs - for his help/advice. Twitter: @mame82
* Bastille Threat Research Team - [RFStorm nRF24LU1+ Research Firmware](https://github.com/BastilleResearch/nrf-research-firmware) 
* Robin2 - [Arduino examples for the NRF24L01](https://forum.arduino.cc/index.php?topic=421081.0)

Thanks for their work to all of them.

## Introduction

This library was written to play with the nRF24L01 Transceiver using a BusPirate. It's based on and old project by Kevin Mehall [nRF24L01-buspirate](https://github.com/kevinmehall/nRF24L01-buspirate)

For a full explanation of this library you can check the blog post that I've written and it's included in this Repository.

## Included examples

I've included several examples to test this library using an Arduino board as sender/receiver on one side of the communications and the BusPirate with the nRF24L01 in the other.

For example, you can upload the code found in "Arduino_tests/SimpleReceiver" in the Arduino (I've tested it with Mega and Uno as well), and run the Python script in "examples/test_tx.py"

The Arduino examples were found in the Arduino Forum, by the user Robin2 - [Arduino examples for the NRF24L01](https://forum.arduino.cc/index.php?topic=421081.0).
