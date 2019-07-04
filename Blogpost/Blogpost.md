# Toying with the NRF24L01 Transceiver and Logitech keyboards  

## Introduction

During this blog post I'll try to explain what I've learned during the last months playing with [Nordic's NRF24L01 Transceiver](https://www.nordicsemi.com/Products/Low-power-short-range-wireless/nRF24-series). I'm also sharing some code that I've been working on during this project.

__Note:__ A lot of this project it's based on the work/projects of the following people:

* Kevin Mehall - [nRF24L01-buspirate](https://github.com/kevinmehall/nRF24L01-buspirate)
* Samy Kamkar - [KeySweeper] (https://github.com/samyk/keysweeper)
* Travis Goodspeed - [Original research to enable sniffing for the NRF24L01](https://travisgoodspeed.blogspot.com/2011/02/promiscuity-is-nrf24l01s-duty.html)
* Marcus Mengs - for his help/advice. Twitter: @mame82
* Bastille Threat Research Team - [RFStorm nRF24LU1+ Research Firmware](https://github.com/BastilleResearch/nrf-research-firmware) 
* Robin2 - [Arduino examples for the NRF24L01](https://forum.arduino.cc/index.php?topic=421081.0)

## Motivation

All the motivation to play with the NRF24L01 came from my idea of reproducing the vulnerability reported in [this advisory](https://packetstormsecurity.com/files/138101/Logitech-K520-Crypto-Issues-Replay-Attacks.html).
I wanted to be able to capture and replay the keystrokes as described in the advisory, to accomplish this my idea was to use the following [NRF24L01 module](https://www.amazon.com/MakerFocus-NRF24L01-Transceiver-Antistatic-Compatible/dp/B01IK78PQA/ref=pd_lpo_sbs_147_t_2?_encoding=UTF8&psc=1&refRID=MZ7HYZ5PWTQCAH02395C).

I didn't want to use the Logitech dongle with the custom firmware developed by the Bastille Threat Research Team as another of my goals was to be able to control the NRF24L01 module with the [BusPirate](http://dangerousprototypes.com/blog/bus-pirate-manual/) and discover if this crazy idea was possible or not.

## Prework

As I didn't have any idea of how the module worked after doing some lame tries to make it work without understanding anything (shame on me), I've decided to download the [datasheet](https://www.sparkfun.com/datasheets/Components/SMD/nRF24L01Pluss_Preliminary_Product_Specification_v1_0.pdf) and understand how this device worked.

Before trying to eavesdrop the communications between the keyboard and its dongle I thought that I should know how the nRF24L01  worked under normal circumstances. For this I used two Arduinos and made them "talk" with each other using two modules. I've connected them in the following way:

nRF24L01 Pinout:

![Pinout](Images/nRF24L01-Pinout.png)

| Arduino Mega | nRF24L01   | Arduino UNO |
|--------------|:----------:|-------------|
|09            | CE         | 09          |
|10            | CSN        | 10          |
|50            | MISO       | 12          |
|51            | MOSI       | 11          |
|52            | SCK        | 13          |
|GND           | GND        | GND         |


I've used an external power source (3.3v) to power the nRF24L01.

### Sending and receiving packets in Arduino

To receive packets in the Arduino board I used some example that I found in the following [forum](https://forum.arduino.cc/index.php?topic=421081.0). The most basic example is "Simple receiver" and "Simple Sender". I programmed both Arduinos with these examples and tested that everything worked well.

There are other "more advanced" examples that support dynamic sizes for the Payloads sent (dynamic_payloads_receiver and dynamic_payloads_sender in the Arduino examples folder).

## Introducing nrf24L01-Pirate

Once I could make these simple examples work I've decided to start playing with the nRF24L01 module and Python. To accomplish this I used the BusPirate to Interface the module with the computer. I've found some [old library](https://github.com/kevinmehall/nRF24L01-buspirate) that allowed basic control of the device.

After trying to make it work and failing miserably, I've decided to write my own library, the nrf24L01-Pirate, based on the previous one.

nrf24L01-Pirate link: (https://github.com/nahueldsanchez/nrf24L01-Pirate)

The library supports the following features:

    * Send and receive data
    * Support for static and dynamic payloads
    * Promiscuous mode (Based on Travis Goodspeed ideas)
    * Support to receive Payloads in ACK responses

Originally, I just wanted to reproduce the vulnerabilities explained in the advisory mentioned before, but once I started to write the library I've continued adding support for other features too. I ended up with some (more or less) usable library, not just to try to reproduce the vulnerabilities but for general use as well.

I've written a few examples in Python to communicate with the Arduino examples. As a simple test, you can execute the Python script "test_rx.py" (in the examples folder) and use the "simple Sender" code for the Arduino.

To connect the nRF24L01 to the BusPirate, I've used the wiring provided by Kevin Mehall in his [Repository](https://github.com/kevinmehall/nRF24L01-buspirate#pinout-for-the-itead-module).

| BusPirate    | nRF24L01   |
|--------------|:----------:|
|3.3v          | VCC        |
|AUX           | CE         |
|CS            | CSN        |
|CLK           | CLK        |
|MOSI          | MOSI       |
|MISO          | MISO       |

The library has some comments in the source code that explain some decisions that I made when coding it. This could be useful for someone else trying to reproduce my results or simply trying to play with this device.

## Sniffing the Logitech K520 Keyboard

### nRF24L01 Promiscuous mode

Once I was able to test the nrf24L01-Pirate library with the Arduino examples, I decided to continue working on my main goal.

After reading the excellent post in [Travis Goodspeed's blog](https://travisgoodspeed.blogspot.com/2011/02/promiscuity-is-nrf24l01s-duty.html), I followed these steps to try to find the keyboard address:

1) Put the nRF24L01 in Promiscuous mode (method "enter_promiscuous_mode()", for a full example check the script "nrf24l01_scanner.py).

2) Disconnect the Keyboard's receiver (Logitech Unifying dongle) from the PC.

3) Start pressing keys in the keyboard during some minutes to try to find the valid keyboard address.

This method had two problems:

1) It produced a lot of noise due to the amount of invalid packets that are received. This can be solved capturing lots of packets and trying to find the address that appears more often (As suggested by Travis).

2) The address found was not valid. __WTF!!?__

Once I solved the first problem, I was able to find an address similar to this one __BF:4F:98:A7:00__.

After doing a LOT of testing trying to sniff this address (more on this later) I concluded that the address was not valid. At this point I was stuck a lot of time as I couldn't understand why the address was invalid.

I didn't know what was wrong, it could be my code, the device or simply the keyboard/dongle.

### Finding the keyboard Address

My first idea to find the address was to look for some open source implementation of [Logitech's Unifying software](https://support.logi.com/hc/en-us/articles/360025297913). This software is used to pair devices with unifying dongles. Based on this I assumed that the software could "know" the device address. I've found the [Solaar project](https://pwr.github.io/Solaar/) that allows working with the Unifying receivers on Linux.

The program gave me the same information that I already had (I found the address labeled as "Serial"). I had no luck with this approach, but at least I knew that my library was working.

At this point I was a little bit lost and continued doing testing and playing with my script, but this time with the dongle connected to the machine. After a lot of tests and some luck, __sporadically I found other address: BF:4F:98:A7:12__. The address was almost the same, but the last byte changed. As I had other keyboard to test I paired it with the dongle and repeated the process, finding that the address was almost the same too, but the last byte was __13__.

_It looks like that the dongle assigns addresses sequentially to the different devices that are paired. (I'm not sure about this, I didn't try to confirm it)._

As next step I've decided to use the firmware provided by Bastille Threat Research Team, compatible with Logitech's Unifying dongle model C-U0007, that's based on the Nordic's chip, to check if the addresses that I found with my implementation were correct.

The RFStorm nRF24LU1+ Research Firmware works __MUCH BETTER__ than my code. The [nrf24-scanner.py Python script](https://github.com/BastilleResearch/nrf-research-firmware/blob/02b84d1c4e59c0fb98263c83b2e7c7f9863a3b93/tools/nrf24-scanner.py) found the addresses really quick, and they were the same that I previously found.

#### Notes on the nrf24-scanner script

The first version that I've tried to implement was base on Travis' Goodspeed [goodfet.nrf script](http://goodfet.sourceforge.net/clients/goodfetnrf/). This gave me lots of false positives and the amount of times that the keyboard transmitted packets was low in comparison with the amount of noise, long story short, it didn't work.

After this fail, I've reviewed Bastille's firmware and found the CRC checking that they were doing. I "ported" that code to Python and included it in my script. This worked pretty well and besides the low rate of packet capture compared with the nrf-research-firmware project, the script accomplished its purpose.

### Sniffing the keyboard

I was getting closer to my goal, but I wasn't sure of how to continue. I asked for some [advice](https://twitter.com/nahueldsanchez_/status/1106279731371094016) to Marcus Mengs (@mame82). Thanks for the help!.

Based on his advice I had to perform the following steps:

1) Set the nRF TX mode with the Keyboard address configured.
2) Enable auto ACK and dynamic payloads in the nRF and send a empty payload in the current channel.

Now two things could happen:

1) I could receive an ACK from the dongle, which will mean that I'm in the correct channel. If this happened I could go back to RX mode and wait to receive packets from the keyboard.
2) I could receive an ACK. This means that I was in the incorrect channel. I've had to change the channel and resend the payload.

With his advice in mind, I've developed the script "nrf24l01_sniffer.py" (Almost a port of nrf24-sniffer.py from Bastille).

The script works as PoC, it captures some of the keys pressed in the keyboard but not all of them. For a fully working version, you should use the code provide in the nrf-research-firmware project.

## Conclusions and future work

Developing this library I've learned a lot about the nRF24L01, which was my primary goal. The code is not 100% functional but was useful to better understand how easy could be eavesdrop communications between the keyboard and the its dongle.

This library also could be useful for common uses too, like communicating with Arduino boards.

Still I've to finish implementing the replay attack explained in the advisory, but as my code isn't capable of capturing all the keystrokes I'm not sure if this will be possible.
