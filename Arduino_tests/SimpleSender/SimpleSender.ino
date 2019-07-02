//Example taken from: https://forum.arduino.cc/index.php?topic=421081.0
//Author: Robin2
// SimpleTx - the master or the transmitter

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include "printf.h"


#define CE_PIN   9
#define CSN_PIN  10

const byte slaveAddress[5] = {'R','x','A','A','A'};


RF24 radio(CE_PIN, CSN_PIN); // Create a Radio

char dataToSend[10] = "Message 0";
char txNum = '0';


unsigned long currentMillis;
unsigned long prevMillis;
unsigned long txIntervalMillis = 1000; // send once per second
//unsigned long txIntervalMillis = 200; // send once per second


void setup() {

    Serial.begin(9600);
    pinMode(53,OUTPUT); //Arduino mega SS

    printf_begin();

    Serial.println("SimpleTx Starting");

    radio.begin();
    //RF24_2MBPS
    //RF24_250KBPS
    radio.setDataRate( RF24_2MBPS );
    unsigned int pl = radio.getPayloadSize();
    radio.setPayloadSize(10);
    Serial.print("Payload size: ");
    Serial.println(pl);
    //radio.setRetries(3,5); // delay, count
    radio.openWritingPipe(slaveAddress);
    //radio.setChannel(5);
    radio.printDetails();
    
}

//====================

void loop() {
    currentMillis = millis();
    if (currentMillis - prevMillis >= txIntervalMillis) {
        send();
        prevMillis = millis();
    }
}

//====================

void send() {

    bool rslt;
    rslt = radio.write( &dataToSend, sizeof(dataToSend));
        // Always use sizeof() as it gives the size as the number of bytes.
        // For example if dataToSend was an int sizeof() would correctly return 2

    Serial.print("Data Sent ");
    Serial.print(dataToSend);
    if (rslt) {
        Serial.println("  Acknowledge received");
        updateMessage();
    }
    else {
        Serial.println("  Tx failed");
    }
}

//================

void updateMessage() {
        // so you can see that new data is being sent
    txNum += 1;
    if (txNum > '9') {
        txNum = '0';
    }
    dataToSend[8] = txNum;
}
