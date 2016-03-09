/*
 *sensor to analog0; 5v feed (red); ground (black)
 */

int last = 1000;
void setup() 
{
  Serial.begin(9600);
  Serial.print("Loaded setup");
}

void DoMeasurement()
{
// measure magnetic field
  int raw = analogRead(0);   // Range : 0..1024
  Serial.println(raw);

}

void loop() 
{
    int raw = analogRead(0);
  // if the sensor reading is greater than the threshold:
  if (raw <= 2) {
     Serial.println("Door open!  Hall output is: " + String(raw) + "Spencer is a rat!");
  }
    delay(100);
}
