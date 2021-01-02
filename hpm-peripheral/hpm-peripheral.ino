/*
   This reads a pair of Honeywell HPM air quality sensors and makes them available over i2c at address 0x77
   We don't use serial because it's not reliable with a RasPi Zero W on the other side, ask me how long it took to learn this!
   AKA 2021, made in 2020 for dennis
   Sample data:
   AQI 56  PM 1.0 = 16, PM 2.5 = 18, PM 4.0 = 21, PM 10.0 = 21
   AQI 55  PM 1.0 = 15, PM 2.5 = 17, PM 4.0 = 20, PM 10.0 = 20
   AQI 54  PM 1.0 = 14, PM 2.5 = 16, PM 4.0 = 18, PM 10.0 = 18
   etc.
*/
#include <HPMA115_Compact.h>
#include <i2c_t3.h>

// Function prototypes
void receiveEvent(size_t count);
void requestEvent(void);

// Memory
#define MEM_LEN 256
char databuf[MEM_LEN];
char inbuf[MEM_LEN];
volatile uint8_t received;


// Possible pins for connecting to the HPM.
#define UART_TX 2  // to HPM Compact pin 9
#define UART_RX 3  // to HPM Compact pin 7
#define HWSERIAL Serial2
#define HWSERIAL2 Serial3
#define I2C_ADDRESS 0x77
#define DEBUG 1
// Remember that there are two varieties of the Honeywell HPM115:
// A "standard" and a "compact". They return different auto-read data messages.
HPMA115_Compact hpm = HPMA115_Compact();
HPMA115_Compact hpm2 = HPMA115_Compact();

// Helper function to print current measurement results.
void printResults();
int aqi[2];
int pm1[2];
int pm25[2];
int pm4[2];
int pm10[2];

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  if (DEBUG) {
    // debug output on serial1
    Serial.begin(HPMA115_BAUD);
  }
  // sensor A on Serial2
  HWSERIAL.begin(HPMA115_BAUD);
  // sensor B on Serial3
  HWSERIAL2.begin(HPMA115_BAUD);
  // Setup for Slave mode, address 0x77, pins 18/19, external pullups, 400kHz
  Wire.begin(I2C_SLAVE, I2C_ADDRESS, I2C_PINS_18_19, I2C_PULLUP_EXT, 400000);
  // Data init
  received = 0;
  memset(databuf, 0, sizeof(databuf));
  memset(inbuf, 0, sizeof(inbuf));
  // register events
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  aqi[0] = 0;
  aqi[1] = 0;
  pm1[0] = 0;
  pm1[1] = 0;
  pm4[0] = 0;
  pm4[1] = 0;
  pm10[0] = 0;
  pm10[1] = 0;
  pm25[0] = 0;
  pm25[1] = 0;
  // Configure the HPM device to use our data stream.
  // (Note carefully the '&' in the next line.)
  hpm.begin(&HWSERIAL);
  hpm2.begin(&HWSERIAL2);
  hpm.startAutoSend();
  hpm2.startAutoSend();
}

void loop() {
  // print received data - this is done in main loop to keep time spent in I2C ISR to minimum
  if (received)
  {
    digitalWrite(LED_BUILTIN, HIGH);
    if (DEBUG > 1) {
      Serial.printf("I received: '%s'\n", inbuf);
    }
    received = 0;
    requestEvent();
    digitalWrite(LED_BUILTIN, LOW);
  }

  if (hpm.isNewDataAvailable() && hpm2.isNewDataAvailable()) {
    // No error, so the data was updated automatically
    takeReading();
  }

  //  printResults3();
  delay(1000);
}

// take serial reading
void takeReading() {
  aqi[0] = hpm.getAQI();
  aqi[1] = hpm2.getAQI();
  pm1[0] = hpm.getPM1();
  pm1[1] = hpm2.getPM1();
  pm4[0] = hpm.getPM4();
  pm4[1] = hpm2.getPM4();
  pm25[0] = hpm.getPM25();
  pm25[1] = hpm2.getPM25();
  pm10[0] = hpm.getPM10();
  pm10[1] = hpm2.getPM10();
  if (DEBUG > 1) {
    printResults3();
  }
}
