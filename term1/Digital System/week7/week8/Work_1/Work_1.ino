// ข้อที่ 1
void setup() {
  // put your setup code here, to run once:
  pinMode(11, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(11, HIGH);
  delay(200);
  digitalWrite(11, LOW);
  delay(200);
}


//ข้อที่2
int s1 = 4; 
int LED = 13;

void setup() {
  // Initialize button and LED pins
  pinMode(s1, INPUT_PULLUP);
  pinMode(LED, OUTPUT);
}

void loop() {
  // Read the button state
  if (digitalRead(s1) == HIGH) {
    digitalWrite(LED, HIGH);  // Turn on LED when button is pressed
  } else {
    digitalWrite(LED, LOW);   // Turn off LED when button is not pressed
  }
}
