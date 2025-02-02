// Libraries
#include <Servo.h>.

//========================================================================================================
// Defines Tirg and Echo pins of the Ultrasonic Sensor
const int trigPin = 10;
const int echoPin = 11;

// Variables for the duration and the distance
long duration;
int distance;

const int servoPin = 12;
Servo myServo;  // Creates a servo object for controlling the servo motor

//=============================================================================================================
// Function to read the sensor data and calculate the distance
int calculateDistance() {
  digitalWrite(trigPin, LOW);   // Set trig pin to low to ensure a clean pulse
  delayMicroseconds(2);         // Delay for 2 microseconds
  digitalWrite(trigPin, HIGH);  // Send a 10 microsecond pulse by setting trig pin to high
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);  // Set trig pin back to low

  // Measure the pulse width of the echo pin and calculate the distance value
  float distance = pulseIn(echoPin, HIGH) / 58.00;  // Formula: (340m/s * 1us) / 2
  return distance;
}

//========================================================================================================
const int DEFAULT_MODE = 0;
const int BUTTON_MODE = 1;
int current_mode = DEFAULT_MODE;
int speakerPin = 5;

//===============================================================================================================
// Check distance and serialprints
void verifica(int i) {
  myServo.write(i);
  distance = calculateDistance();

  if (distance < 50) {
    digitalWrite(3, HIGH);
    for (int i = 0; i < 10; i++) {
      digitalWrite(speakerPin, HIGH);
      delayMicroseconds(500);
      digitalWrite(speakerPin, LOW);
      delayMicroseconds(500);
    }
    delay(20);
  } else {
    digitalWrite(3, LOW);
    delay(30);
  }
  Serial.print(i);
  Serial.print(",");
  Serial.println(distance);
}

//===============================================================================================================
// Setup
void setup() {
  pinMode(trigPin, OUTPUT);  // Sets the trigPin as an Output
  pinMode(echoPin, INPUT);   // Sets the echoPin as an Input
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(speakerPin, OUTPUT);
  pinMode(A5, INPUT);

  Serial.begin(9600);
  myServo.attach(servoPin);  // Defines on which pin is the servo motor attached
}

//===============================================================================================================
// Loop
void loop() {
  /*if (Serial.available() > 0) {
        command = Serial.readStringUntil('\n');
        if (command == "DEFAULT") current_mode=DEFAULT_MODE;
        if (command == "BUTTON") current_mode=BUTTON_MODE;  // Stop sending data
    }*/
  if (current_mode == DEFAULT_MODE) {  // Default mode is idle, turned off
    //Leds off
    digitalWrite(2, LOW);
    digitalWrite(3, LOW);
    digitalWrite(5, LOW);

    // Servo in the middle
    myServo.write(90);
    delay(30);

    Serial.print(90);
    Serial.print(",");
    Serial.println(1000);

    if (digitalRead(A5) == HIGH) {
      current_mode = BUTTON_MODE;
      delay(500);
    }

  } else {
    if (current_mode == BUTTON_MODE) {
      // Green Led on
      digitalWrite(2, HIGH);

      // rotates the servo motor from 15 to 165 degrees
      for (int i = 90; i <= 165; i++) {
        verifica(i);
        if (digitalRead(A5) == HIGH) {
          current_mode = DEFAULT_MODE;
          delay(500);
          return;
        }
      }
      for (int i = 165; i > 15; i--) {
        verifica(i);
        if (digitalRead(A5) == HIGH) {
          current_mode = DEFAULT_MODE;
          delay(500);
          return;
        }
      }
      for (int i = 15; i <= 90; i++) {
        verifica(i);
        if (digitalRead(A5) == HIGH) {
          current_mode = DEFAULT_MODE;
          delay(500);
          return;
        }
      }
    }
  }
}
