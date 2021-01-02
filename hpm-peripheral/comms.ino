//
// handle Rx Event (incoming I2C data)
//
void receiveEvent(size_t count)
{
  if (DEBUG > 1) {
    Serial.print("received i2c event");
  }
  Wire.read(inbuf, count);  // copy Rx data to inbuf
  received = count;           // set received flag to count, this triggers print in main loop
}

//
// handle Tx Event (outgoing I2C data)
//
void requestEvent(void)
{
  sprintf(databuf, "%04i|%04i|%04i|%04i|%04i|%04i", aqi[0], aqi[1], pm25[0], pm25[1], pm4[0], pm4[1]);
  if (DEBUG) {
    Serial.println(databuf);
  }
  Wire.write(databuf, MEM_LEN); // fill Tx buffer (send full mem)
}
