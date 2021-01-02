
void printResults() {
  Serial.print("~1~ AQI ");
  Serial.print(hpm.getAQI());
  //  Serial.print("  PM 1.0 = ");
  //  Serial.print(hpm.getPM1());
  Serial.print(", PM 2.5 = ");
  Serial.print(hpm.getPM25());
  //  Serial.print(", PM 4.0 = ");
  //  Serial.print(hpm.getPM4());
  Serial.print(", PM 10.0 = ");
  Serial.println(hpm.getPM10());
}

void printResults2() {
  Serial.print("~2~ AQI ");
  Serial.print(hpm2.getAQI());
  Serial.print("  PM 1.0 = ");
  Serial.print(hpm2.getPM1());
  Serial.print(", PM 2.5 = ");
  Serial.print(hpm2.getPM25());
  Serial.print(", PM 4.0 = ");
  Serial.print(hpm2.getPM4());
  Serial.print(", PM 10.0 = ");
  Serial.println(hpm2.getPM10());
}

void printResults3() {
//  int n;
//  n = sprintf(databuf, "%04i %04i %04i %04i %04i %04i", aqi[0], aqi[1], pm25[0], pm25[1], pm4[0], pm4[1]);
//  requestEvent();
////  Serial.println(databuf);
////
  Serial.print("AQI ");
  Serial.print(aqi[0]);
  Serial.print("-");
  Serial.print(aqi[1]);
  Serial.print(", PM 1.0 ");
  Serial.print(pm1[0]);
  Serial.print("-");
  Serial.print(pm1[1]);
  Serial.print(", PM 2.5 ");
  Serial.print(pm25[0]);
  Serial.print("-");
  Serial.print(pm25[1]);
  Serial.print(", PM 4.0 ");
  Serial.print(pm4[0]);
  Serial.print("-");
  Serial.print(pm4[1]);
  Serial.print(", PM 10.0 ");
  Serial.print(pm10[0]);
  Serial.print("-");
  Serial.println(pm10[1]);
}
