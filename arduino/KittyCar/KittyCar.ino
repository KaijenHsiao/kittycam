String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

void setup() {
  // initialize serial:
  Serial.begin(9600);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);
  
  // pin 13 triggers the Frolic BOLT
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
  
  // pin 12 triggers the auto-feeder
  pinMode(12, OUTPUT);
  digitalWrite(12, LOW);
}

void loop() {
  if (stringComplete) {
    
    if (inputString[0] == 't'){
      digitalWrite(13, HIGH);
      delay(100);
      digitalWrite(13, LOW);
    }
    else if(inputString[0] == 's'){
      digitalWrite(12, HIGH);
      delay(5000);
      digitalWrite(12, LOW);
    }
    //Serial.println(inputString); 
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
}

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    } 
  }
}


