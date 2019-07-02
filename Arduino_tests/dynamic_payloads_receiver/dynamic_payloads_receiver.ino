//Example taken from: https://forum.arduino.cc/index.php?topic=421081.0
//Author: Robin2

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include "printf.h"


#define CE_PIN   9
#define CSN_PIN  10

const byte slaveAddress[5] = {'R','x','A','A','A'};


RF24 radio(CE_PIN, CSN_PIN); // Create a Radio


const int max_payload_size = 32;
char receive_payload[max_payload_size+1]; // +1 to allow room for a terminating NULL char

void setup() {

    Serial.begin(9600);
    pinMode(53,OUTPUT); //Arduino mega SS

    printf_begin();

    Serial.println("Dynamic payloads receiver Starting");
    radio.begin();
    radio.setDataRate( RF24_2MBPS );
    radio.enableDynamicPayloads();
    radio.openReadingPipe(1, slaveAddress);
    radio.startListening();
    radio.printDetails();
}

//====================

void loop() {
  while ( radio.available() )
      {
        // Fetch the payload, and see if this was the last one.
        uint8_t len = radio.getDynamicPayloadSize();
        
        // If a corrupt dynamic payload is received, it will be flushed
        if(!len){
          continue; 
        }
        
        radio.read( receive_payload, len );
  
        // Put a zero at the end for easy printing
        receive_payload[len] = 0;
  
        // Spew it
        Serial.print(F("Got response size="));
        Serial.print(len);
        Serial.print(F(" value="));
        Serial.println(receive_payload);
  
        // First, stop listening so we can talk
        radio.stopListening();
  
        // Send the final one back.
        radio.write( receive_payload, len );
        Serial.println(F("Sent response."));
  
        // Now, resume listening so we catch the next packets.
        radio.startListening();
      }
 }
