//int ledPin = 13;
//char buf[100], outputBuffer[100];
//int i, retValOn, retValOff;
//
//void setup() {
//  //pinMode(ledPin, OUTPUT);
//  Serial.begin(9600);
//
//}
//
//void loop() {
//  i = 0;
//  //digitalWrite(ledPin, HIGH);
//  //delay(100);
//  //digitalWrite(ledPin, LOW);
//  //delay(100);
//
//  memset(buf, 0, sizeof buf);
//
//  if (Serial.available() > 0) {
//    delay(1000);
//  }
//
//  while (Serial.available() > 0){
//    buf[i++] = (char)Serial.read();
//  }
//
//  buf[i-1] = 0;
//
//  if (i) {
//    if ((retValOn = strcmp(buf, "Switch on")) == 0) {
//      digitalWrite(ledPin, HIGH);
//    } else if ((retValOff = strcmp(buf, "Switch off")) == 0) {
//      digitalWrite(ledPin, LOW);
//    } else {
//      sprintf(outputBuffer, "ReturnVal1: %i, ReturnVal2: %i, string: '%s'", retValOn, retValOff, buf);
//      Serial.print(outputBuffer);
//    }
//  }
//}

int ledPin = 13;
char input;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0){
    if ((input = Serial.read()) == 'a') {
      digitalWrite(ledPin, HIGH);
    } else if (input == 'b') {
      digitalWrite(ledPin, LOW);
    }
  }
}
