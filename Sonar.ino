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
const int AUTO_MODE = 1;
const int MANUAL_MODE = 2;
int current_mode = DEFAULT_MODE;
int speakerPin = 5;
String command;
int delay_time = 100;
int max_distance = 50;
bool Buzzer = true;
int ite = 90;
bool crescente = true;

//===============================================================================================================
// Check distance and serialprints
void verifica(int j, int max, bool buzzer) {
  myServo.write(j);
  distance = calculateDistance();

  if (distance < max) {
    digitalWrite(3, HIGH);
    if (buzzer == true) {
      for (int i = 0; i < 30; i++) {
        digitalWrite(speakerPin, HIGH);
        delayMicroseconds(500);
        digitalWrite(speakerPin, LOW);
        delayMicroseconds(500);
      }
      delay(max(10, delay_time - 30));
    } else {
      delay(delay_time);
    }
  } else {
    digitalWrite(3, LOW);
    delay(delay_time);
  }
  Serial.print(j);
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
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    command.trim();
    if (!isDigit(command.charAt(0))) {
      if (command == "DEFAULT"){
         current_mode = DEFAULT_MODE;
         ite = 90;
         crescente = true;
      }
      if (command == "AUTO"){
         current_mode = AUTO_MODE;
         ite = 90;
         crescente = true;
      }
      if (command == "MANUAL"){
         current_mode = MANUAL_MODE;
         ite = 90;
         crescente = true;
      }
      if (command == "BUZZ_ON") Buzzer = true;
      if (command == "BUZZ_OFF") Buzzer = false;
      
    }
  }
  if (current_mode == DEFAULT_MODE) {  // Default mode is idle, turned off
    //Leds off
    digitalWrite(2, LOW);
    digitalWrite(3, LOW);
    digitalWrite(5, LOW);

    // Servo in the middle
    myServo.write(90);
    delay(delay_time);

    Serial.print(90);
    Serial.print(",");
    Serial.println(1000);

    if (digitalRead(A5) == HIGH) {
      current_mode = AUTO_MODE;
      Serial.println("AUTO");
      delay(500);
    }

  } else if (current_mode == AUTO_MODE) {
    // Green Led on
    digitalWrite(2, HIGH);

    verifica(ite, 50, Buzzer);
    if (digitalRead(A5) == HIGH) {
      current_mode = DEFAULT_MODE;
      Serial.println("DEFAULT");
      ite = 90;
      crescente==true;
      delay(500);
      return;
    }
    if (ite==165) crescente=false;
    if (ite==15) crescente=true; 
    if ((ite<165) && crescente==true) ite++;
    if ((ite>15) && crescente==false) ite--;

  } else if (current_mode == MANUAL_MODE) {
    digitalWrite(2, HIGH);

    verifica(90, 50, Buzzer);
    if (digitalRead(A5) == HIGH) {
      current_mode = DEFAULT_MODE;
      Serial.println("DEFAULT");
      delay(500);
      return;
    }
  }
}
