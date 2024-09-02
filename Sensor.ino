#include <Wire.h>

const int MPU_ADDR = 0x68; // MPU-6050 I2C address (AD0 pin is connected to GND)

int16_t accelX, accelY, accelZ;
int16_t gyroX, gyroY, gyroZ;
int16_t tempRaw;

void setup() {
  Wire.begin();
  Serial.begin(9600);

  // Initialize MPU6050
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0);    // Set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
}

void loop() {
  // Request sensor data
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B); // Starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 14, true); // Request 14 bytes from MPU-6050

  // Read accelerometer and gyro data
  accelX = (Wire.read() << 8 | Wire.read()); // Combine two bytes from the MPU6050 to form the 16-bit value
  accelY = (Wire.read() << 8 | Wire.read());
  accelZ = (Wire.read() << 8 | Wire.read());
  tempRaw = (Wire.read() << 8 | Wire.read());
  gyroX = (Wire.read() << 8 | Wire.read());
  gyroY = (Wire.read() << 8 | Wire.read());
  gyroZ = (Wire.read() << 8 | Wire.read());

  // Convert gyro data to degrees per second (dps)
  float gyroX_dps = gyroX / 131.0;
  float gyroY_dps = gyroY / 131.0;
  float gyroZ_dps = gyroZ / 131.0;

  // Integrate the gyroZ_dps to get the yaw angle
  static float yaw = 0;
  yaw += gyroZ_dps * (millis() - previousTime) / 1000.0;
  previousTime = millis();

  // Print the yaw angle
  Serial.print("Yaw: ");
  Serial.println(yaw);

  delay(100); // Delay for a while to see the output
}
