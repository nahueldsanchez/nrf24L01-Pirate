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

const int min_payload_size = 4;
const int max_payload_size = 32;
const int payload_size_increments_by = 1;
int next_payload_size = min_payload_size;

char receive_payload[max_payload_size+1]; // +1 to allow room for a terminating NULL char

void setup() {

    Serial.begin(9600);
    pinMode(53,OUTPUT); //Arduino mega SS

    printf_begin();

    Serial.println("Dynamic payloads sender Starting");

    radio.begin();
    //RF24_2MBPS
    //RF24_250KBPS
    radio.setDataRate( RF24_2MBPS );
    radio.enableDynamicPayloads();
    radio.openWritingPipe(slaveAddress);
    radio.printDetails();
    
}

//====================

void loop() {
// The payload will always be the same, what will change is how much of it we send.
    static char send_payload[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ789012";
    bool rslt;
    
    // Take the time, and send it.  This will block until complete
    Serial.print(F("Now sending length "));
    Serial.println(next_payload_size);
    rslt = radio.write( send_payload, next_payload_size );

    if (rslt) {
        Serial.println("  Acknowledge received");
        // Update size for next time.
        next_payload_size += payload_size_increments_by;
        if ( next_payload_size > max_payload_size )
            next_payload_size = min_payload_size;
    }
    else {
        Serial.println("  Tx failed");
    }

    // Try again 1s later
    delay(1000);
}
