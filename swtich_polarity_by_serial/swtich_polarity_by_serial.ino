int relay4 = 4;
int relay3 = 5;
int relay2 = 6;
int relay1 = 7;
// NO (normally open)
// NC (normally closed)
// COM (common connection)

// relay1: NC DC+
// relay1: NO DC-
// relay2: NC DC-
// relay2: NO DC+
// COM of relay1: output+
// COM of relay2: output-

// positive polarity
// relay1 and 2 are HIGH
// relay1: NC DC+
// relay2: NC DC-

// negative polarity
// relay1 and 2 are LOW
// relay1: NO DC-
// relay2: NO DC+
 
// other cases (in cases of error)
// relay1: NC DC+
// relay2: NO DC+
// this is not a short, so no problem

// the setup routine runs once when you press reset:
void setup()  {
    // declare relay1, relay2 to be an output:
    pinMode(relay1, OUTPUT);
    pinMode(relay2, OUTPUT);
    Serial.begin(115200);
}

// the loop routine runs over and over again forever:
void loop()  {
  int prevRelayHL = 0;
  int relayHL = 0;
  while (true) {
    int readValue = analogRead(A4);

    prevRelayHL = relayHL;
    if (readValue > 500) {
      relayHL = 1;
    } else {
      relayHL = 0;
    }
    //Serial.println(readValue);
    //Serial.println(relayHL);
    if (prevRelayHL != relayHL) {
      if (relayHL > 0) { // p (lowercase)
          digitalWrite(relay1, HIGH);
          digitalWrite(relay2, HIGH);
          //Serial.println("polarity set to positive");
      } else { // n (lowercase)
          digitalWrite(relay1, LOW);
          digitalWrite(relay2, LOW);
      }
    }
  }
  
}
