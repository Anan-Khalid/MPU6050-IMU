class PID {
  private:
    double kp, ki, kd;
    double prevError;
    double integral;
  public:
    PID(double kp, double ki, double kd) {
      this->kp = kp;
      this->ki = ki;
      this->kd = kd;
      prevError = 0;
      integral = 0;
    }
    double compute(double setpoint, double input) {
      double error = setpoint - input;
      integral += error;
      double derivative = error - prevError;
      prevError = error;
      return kp * error + ki * integral + kd * derivative;
    }
};

class SoftStart {
  private:
    double alpha;
    double prevOutput;
  public:
    SoftStart(double alpha) {
      this->alpha = alpha;
      prevOutput = 0;
    }
    double filter(double input) {
      return alpha * input + (1 - alpha) * prevOutput;
    }
};

const int motorPin = 9;
PID pid(2, 1, 0);
SoftStart softStart(0.9);

void setup() {
  pinMode(motorPin, OUTPUT);
}

void loop() {
  double setpoint = 100; // desired speed
  double input = analogRead(A0); // current speed
  double output = pid.compute(setpoint, input);
  output = softStart.filter(output);
  analogWrite(motorPin, output);
  delay(50);
}