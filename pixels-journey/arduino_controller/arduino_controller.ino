const int buttonPin1 = 2; // Button for Jump
const int buttonPin2 = 4; // Button for Left
const int buttonPin3 = 3; // Button for Right

void setup() {
  pinMode(buttonPin1, INPUT_PULLUP);
  pinMode(buttonPin2, INPUT_PULLUP);
  pinMode(buttonPin3, INPUT_PULLUP);
  Serial.begin(9600);

}

void loop() {
  if (digitalRead(buttonPin1) == LOW) {
      Serial.println("JUMP");
      delay(10);  // Debounce delay
  }
  if (digitalRead(buttonPin2) == LOW) {
      Serial.println("LEFT");
      delay(10);
  }
  if (digitalRead(buttonPin3) == LOW) {
      Serial.println("RIGHT");
      delay(10);
  }
}
