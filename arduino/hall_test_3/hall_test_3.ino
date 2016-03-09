/*
 *sensor to analog0; 5v feed (red); ground (black)
 */
 
//from example provided with Rand A
#include "RAComm.h"       // Use Raspberry command library

#define CMD1 "GetRTC -s"  // get timestamp

#define LOGFILE  "/home/pi/wakeup.dat"  // where to write message

#define CHECKTIME 10000    // check interval 10 sec

RAComm Cmd;               // Cmd is the RAComm class

int status=0;          // status flag (when condition true, set flag 1)
                       // it doesn't restart procedure until status will be back to 0
boolean flagOn;        // flag Raspberry on or off

int sensorPin = A1;    // select the input pin for the potentiometer or photores
int ledPin = 13;       // select the pin for the LED
int sensorValue = 0;   // variable to store the value coming from the sensor
int threshold =2;    // threshold of sensorPin 
int switchPin = 4;     // pin for switching 

long ta=0;

void setup() {
  pinMode(ledPin, OUTPUT);     // led just as flag
  pinMode(switchPin, OUTPUT);  
  digitalWrite(ledPin,0);      // led off
  digitalWrite(switchPin,0);   // initialize switching pin

  Serial.begin(9600);
  Serial.print("Loaded setup");
}

void loop() 
{
    int raw = analogRead(sensorPin);
  // if the sensor reading is greater than the threshold:
  if (raw <= threshold) {
     Serial.println("Door open!  Hall output is: " + String(raw) + " Spencer is a rat!");
     digitalWrite(switchPin,HIGH);
     Serial.println("Switching pi on ...");
  }
    delay(100);
}
