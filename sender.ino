#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <SPI.h>
#include <SD.h>

// Create an instance of the BNO055 sensor with the correct I2C address
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);  // Specify the I2C address here (0x28)

// SD card chip select pin
const int chipSelect = BUILTIN_SDCARD;

// Variables to store GPS data (Example: NMEA sentences can be parsed similarly)
float latitude = 0.0;
float longitude = 0.0;
float altitude = 0.0;
int satellites = 0;

// File object for the SD card
File dataFile;

// Filename for data logging
const char* DATA_FILE = "data.csv";

void writeHeadersIfNewFile() {
  // Check if file doesn't exist
  if (!SD.exists(DATA_FILE)) {
    // Open the file in write mode
    dataFile = SD.open(DATA_FILE, FILE_WRITE);
    
    if (dataFile) {
      // Write CSV headers only if it's a new file
      dataFile.println("Timestamp_ms,Accel_X_ms2,Accel_Y_ms2,Accel_Z_ms2,Gyro_X_radps,Gyro_Y_radps,Gyro_Z_radps,Mag_X_uT,Mag_Y_uT,Mag_Z_uT,Latitude_deg,Longitude_deg,Altitude_m");
      
      dataFile.close();
      Serial.println("Headers written to new CSV file.");
    } else {
      Serial.println("Error creating file for headers.");
    }
  }
}

void setup() {
  Serial.begin(9600);  // USB Serial communication for debugging
  Serial2.begin(9600); // Bluetooth Serial communication at 9600 baud (via Serial2)
  Serial1.begin(9600); // GPS module on Serial1
  
  Wire.begin();

  // Initialize the SD card
  if (!SD.begin(chipSelect)) {
    Serial.println("SD card initialization failed!");
    while (1);
  }
  Serial.println("SD card initialized.");

  // Initialize the BNO055 sensor
  if (!bno.begin()) {
    Serial.println("Couldn't find the sensor!");
    while (1);
  }
  Serial.println("BNO055 and Bluetooth initialized.");

  // Write headers only if it's a new file
  writeHeadersIfNewFile();
}

// Function to parse GPGGA sentence from GPS
void parseGPGGA(String sentence) {
  int startIdx = sentence.indexOf("$GPGGA,") + 7;
  String ggaData = sentence.substring(startIdx);
  int commaIndex = ggaData.indexOf(',');

  // Get latitude
  String latStr = ggaData.substring(0, commaIndex);
  latitude = latStr.toFloat();

  // Get longitude
  ggaData = ggaData.substring(commaIndex + 1);
  commaIndex = ggaData.indexOf(',');
  String lonStr = ggaData.substring(0, commaIndex);
  longitude = lonStr.toFloat();

  // Get altitude
  ggaData = ggaData.substring(commaIndex + 1);
  commaIndex = ggaData.indexOf(',');
  String altStr = ggaData.substring(0, commaIndex);
  altitude = altStr.toFloat();
}

void loop() {
  // Create sensor event objects for each type of measurement
  sensors_event_t accelEvent, gyroEvent, magEvent;

  // Get accelerometer, gyroscope, and magnetometer data
  bno.getEvent(&accelEvent, Adafruit_BNO055::VECTOR_ACCELEROMETER);
  bno.getEvent(&gyroEvent, Adafruit_BNO055::VECTOR_GYROSCOPE);
  bno.getEvent(&magEvent, Adafruit_BNO055::VECTOR_MAGNETOMETER);

  // Send accelerometer data over USB serial
  Serial.print("Acceleration - X: ");
  Serial.print(accelEvent.acceleration.x);
  Serial.print(", Y: ");
  Serial.print(accelEvent.acceleration.y);
  Serial.print(", Z: ");
  Serial.println(accelEvent.acceleration.z);

  // Send gyroscope data over USB serial
  Serial.print("Gyroscope - X: ");
  Serial.print(gyroEvent.gyro.x);
  Serial.print(", Y: ");
  Serial.print(gyroEvent.gyro.y);
  Serial.print(", Z: ");
  Serial.println(gyroEvent.gyro.z);

  // Send magnetometer data over USB serial
  Serial.print("Magnetic Field - X: ");
  Serial.print(magEvent.magnetic.x);
  Serial.print(", Y: ");
  Serial.print(magEvent.magnetic.y);
  Serial.print(", Z: ");
  Serial.println(magEvent.magnetic.z);

  // Send accelerometer data over Bluetooth (Serial2)
  Serial2.print("Acceleration - X: ");
  Serial2.print(accelEvent.acceleration.x);
  Serial2.print(", Y: ");
  Serial2.print(accelEvent.acceleration.y);
  Serial2.print(", Z: ");
  Serial2.println(accelEvent.acceleration.z);

  // Send gyroscope data over Bluetooth (Serial2)
  Serial2.print("Gyroscope - X: ");
  Serial2.print(gyroEvent.gyro.x);
  Serial2.print(", Y: ");
  Serial2.print(gyroEvent.gyro.y);
  Serial2.print(", Z: ");
  Serial2.println(gyroEvent.gyro.z);

  // Send magnetometer data over Bluetooth (Serial2)
  Serial2.print("Magnetic Field - X: ");
  Serial2.print(magEvent.magnetic.x);
  Serial2.print(", Y: ");
  Serial2.print(magEvent.magnetic.y);
  Serial2.print(", Z: ");
  Serial2.println(magEvent.magnetic.z);

  // Read GPS data from Serial1 (if available)
  if (Serial1.available()) {
    String gpsData = Serial1.readStringUntil('\n');
    if (gpsData.indexOf("$GPGGA") >= 0) {
      parseGPGGA(gpsData);

      // Send GPS data via Bluetooth
      Serial2.print("Latitude: ");
      Serial2.print(latitude, 4);
      Serial2.print(", Longitude: ");
      Serial2.print(longitude, 4);
      Serial2.print(", Elevation: ");
      Serial2.print(altitude);
      Serial2.print(", Satellites: ");
      Serial2.println(satellites);
    }
  }

  // Combine sensor and GPS data into a CSV string
  String dataString = String(millis()) + "," + 
                      String(accelEvent.acceleration.x, 3) + "," +
                      String(accelEvent.acceleration.y, 3) + "," +
                      String(accelEvent.acceleration.z, 3) + "," +
                      String(gyroEvent.gyro.x, 3) + "," +
                      String(gyroEvent.gyro.y, 3) + "," +
                      String(gyroEvent.gyro.z, 3) + "," +
                      String(magEvent.magnetic.x, 3) + "," +
                      String(magEvent.magnetic.y, 3) + "," +
                      String(magEvent.magnetic.z, 3) + "," +
                      String(latitude, 6) + "," +
                      String(longitude, 6) + "," +
                      String(altitude, 2);

  // Write data to SD card
  dataFile = SD.open(DATA_FILE, FILE_WRITE);
  if (dataFile) {
    dataFile.println(dataString);
    dataFile.close();
  } else {
    Serial.println("Error opening file for writing.");
  }

  delay(1000); // Adjust delay as needed
}