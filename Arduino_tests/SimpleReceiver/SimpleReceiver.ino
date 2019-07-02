//Example taken from: https://forum.arduino.cc/index.php?topic=421081.0
//Author: Robin2
// SimpleRx - the slave or the receiver

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include "printf.h"

#define CE_PIN   9
#define CSN_PIN  10

const byte thisSlaveAddress[5] = {'R','x','A','A','A'};

RF24 radio(CE_PIN, CSN_PIN);

char dataReceived[10]; // this must match dataToSend in the TX
bool newData = false;

//===========

void setup() {

    Serial.begin(9600);
    pinMode(53,OUTPUT); //Arduino mega SS

    printf_begin();

    Serial.println("SimpleRX Starting");
    radio.begin();
    //RF24_1MBPS
    radio.setPayloadSize(1);
    radio.setDataRate( RF24_250KBPS );
    radio.openReadingPipe(1, thisSlaveAddress);
    radio.startListening();
    radio.printDetails();
    
}

//=============

void loop() {
    getData();
    showData();
    /*
    if (radio.testCarrier()){
      Serial.println("Carrier Detected!");
    }
    */
}

//==============

void getData() {
    if ( radio.available() ) {
        radio.read( &dataReceived, sizeof(dataReceived) );
        newData = true;
    }
}

void showData() {
    if (newData == true) {
        Serial.print("Data received ");
        Serial.println(dataReceived);
        newData = false;
    }
}
