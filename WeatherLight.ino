#include <DallasTemperature.h>
#include <OneWire.h>
#include <Adafruit_SI1145.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>
#include <Wire.h>
#include <Adafruit_VEML6075.h>
#include <GUVA-S12SD.h>

/*!
 * @file WeatherLight.ino
 *
 * This sketch combines the adafruit scripts for each of the
 *  boards. It also includes code from ?? for the GUVA-S12SD
 * 
 * Designed specifically to work with the VEML6075 sensor from Adafruit
 * ----> https://www.adafruit.com/products/3964
 *
 * Designed specifically to work with the Si1145 sensor in the Adafruit shop
  ----> https://www.adafruit.com/products/1777
 *
 * These sensors use I2C to communicate, 2 pins (SCL+SDA) are required
 * to interface with the breakout.
 *
 * Adafruit invests time and resources providing this open source code,
 * please support Adafruit and open-source hardware by purchasing
 * products from Adafruit!
 *
 * Written by Limor Fried/Ladyada for Adafruit Industries.  
 *
 * MIT license, all text here must be included in any redistribution.
 *********************
 * TSL2561 code Copyright (C) 2008 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software< /span>
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.

 * Update by K. Townsend (Adafruit Industries) for lighter typedefs, and
 * extended sensor support to include color, voltage and current
 *********************
 * GUVAS-12SD Copyright 2017 Kohei MATSUSHITA
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 
/* This current file is a simple merger of other example files, presented 
 *  to accompany the Wordpress post for completeness.
 *  
 */


// Analogue pins
#define GUVA_PIN 0

#define RAIN_PIN 1
// digital pins
#define PULSE_LIGHT 13
#define ONE_WIRE_BUS 4

Adafruit_VEML6075 uv6075 = Adafruit_VEML6075();
Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);
Adafruit_SI1145 uv1145 = Adafruit_SI1145();

// pin number, voltage, no of times to read
GUVAS12SD uvGuva(GUVA_PIN, 5, 100);

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ds18sensors(&oneWire);

/**************************************************************************
* Displays some basic information on this sensor from the unified         *
*  sensor API sensor_t type (see Adafruit_Sensor for more information)    *
**************************************************************************/
void displayTSLSensorDetails(void)
{
  sensor_t sensor;
  tsl.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" lux");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" lux");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" lux");  
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}

/**************************************************************************
* Configures the gain and integration time for the TSL2561                *
**************************************************************************/
void configureTSLSensor(void)
{
  /* You can also manually set the gain or enable auto-gain support */
  // tsl.setGain(TSL2561_GAIN_1X);      /* No gain ... use in bright light to avoid sensor saturation */
  // tsl.setGain(TSL2561_GAIN_16X);     /* 16x gain ... use in low light to boost sensitivity */
  tsl.enableAutoRange(true);            /* Auto-gain ... switches automatically between 1x and 16x */
  
  /* Changing the integration time gives you better sensor resolution (402ms = 16-bit data) */
  tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_13MS);      /* fast but low resolution */
  // tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_101MS);  /* medium resolution and speed   */
  // tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_402MS);  /* 16-bit data but slowest conversions */

  /* Update these values depending on what you've set above! */  
  Serial.println("------------------------------------");
  Serial.print  ("Gain:         "); Serial.println("Auto");
  Serial.print  ("Timing:       "); Serial.println("13 ms");
  Serial.println("------------------------------------");
}

/**************************************************************************
* ARDUINO setup routine, called once on startup                           *
**************************************************************************/
void setup() {
  pinMode(PULSE_LIGHT, OUTPUT);
  Serial.begin(9600);

  // setup the 6075 sensor *******************************************
  Serial.println("VEML6075 Full Test");
  if (! uv6075.begin()) {
    Serial.println("Failed to communicate with VEML6075 sensor, check wiring?");
  }
  Serial.println("Found VEML6075 sensor");

  // Set the integration constant
  uv6075.setIntegrationTime(VEML6075_100MS);
  // Get the integration constant and print it!
  Serial.print("Integration time set to ");
  switch (uv6075.getIntegrationTime()) {
    case VEML6075_50MS: Serial.print("50"); break;
    case VEML6075_100MS: Serial.print("100"); break;
    case VEML6075_200MS: Serial.print("200"); break;
    case VEML6075_400MS: Serial.print("400"); break;
    case VEML6075_800MS: Serial.print("800"); break;
  }
  Serial.println("ms");
  
  // Set the high dynamic mode
  uv6075.setHighDynamic(false);
  // Get the mode
  if (uv6075.getHighDynamic()) {
    Serial.println("High dynamic reading mode");
  } else {
    Serial.println("Normal dynamic reading mode");
  }

  // Set the mode
  uv6075.setForcedMode(false);
  // Get the mode
  if (uv6075.getForcedMode()) {
    Serial.println("Forced reading mode");
  } else {
    Serial.println("Continuous reading mode");
  }
  // Set the calibration coefficients
  uv6075.setCoefficients(2.22, 1.33,  // UVA_A and UVA_B coefficients
                     2.95, 1.74,  // UVB_C and UVB_D coefficients
                     0.001461, 0.002591); // UVA and UVB responses
                     
  // Setup the tsl sensor ************************************************
  if (!tsl.begin())
  {
    Serial.println("Oops, no TSL2561 detected...");
    Serial.println("Program halting!");
    while(1);
  } else {
    Serial.println("Startup TSL2561 initiated");
  }

  /* Display some basic information on this sensor */
  displayTSLSensorDetails();
  /* Setup the sensor gain and integration time */
  configureTSLSensor();

  // Setup the si1145 sensor ************************************************
  if (! uv1145.begin()) {
    Serial.println("Didn't find Si1145");
    Serial.println("Program halting");
    while(1);
  } else {
    Serial.println("Startup: SI1145 initiated");
  }

  // Setup the dallas ds18b20 sensor ***************************************
  ds18sensors.begin(); // ds18b20

  // Rain sensor requires no setup *****************************************
  Serial.println("End of setup");
  Serial.println("*****************************");
  Serial.println("");
}

/**************************************************************************
* ARDUINO loop routine, called repeatedly                                 *
**************************************************************************/
void loop() {
  char buff[64], buff2[16];
  /* Get a new sensor event tsl2561*/ 
  sensors_event_t event;

  digitalWrite(13, HIGH); // create an 'alive' indicator

  Serial.println("*****************************");
  Serial.println("** Start loop **");
  // TSL2561 sensor *******************************************************
  tsl.getEvent(&event);
  /* Display the results (light is measured in lux) */
  if (event.light)
  {
    Serial.println("== tsl2561 ========");
    //Serial.println(event.light);
    // resolution is 1.00 anyway
    dtostrf(event.light, 2, 0, buff2);
    sprintf(buff, "TSLlux: %s", buff2);
    Serial.println(buff);
  }
  else
  {
    /* If event.light = 0 lux the sensor is probably saturated
       and no reliable data could be generated! */
    Serial.println("TSLerror: Sensor overload");
  }

  // SI1445 sensor  *******************************************************
  Serial.println("== si1145 =======");
  sprintf(buff, "SIvis: %u", uv1145.readVisible());
  Serial.println(buff);
  sprintf(buff, "SIir: %u", uv1145.readIR());
  Serial.println(buff);
  
  float UVindex = uv1145.readUV();
  // the index is multiplied by 100 so to get the
  // integer index, divide by 100!
  UVindex /= 100.0;  
  //Serial.print("UV: ");  Serial.println(UVindex);
  dtostrf(UVindex, 4, 2, buff2);
  sprintf(buff, "SIuv: %s", buff2);
  Serial.println(buff);

  // GUVA analogue sensor *************************************************
  Serial.println("== Guva   =======");
  float mV = uvGuva.read();
  Serial.print("Guva mV: "); Serial.println(mV);
  float uvgIndex = uvGuva.index(mV);
  Serial.print("Guva: ");
  Serial.println(uvgIndex);

  // VEML6075 sensor ******************************************************
  Serial.println("== UV6075 =======");
  Serial.print("VEMLuva: "); Serial.println(uv6075.readUVA());
  Serial.print("VEMLuvb: "); Serial.println(uv6075.readUVB());
  Serial.print("VEMLuvi: "); Serial.println(uv6075.readUVI());

  Serial.println("== Other ===========");
  ds18sensors.requestTemperatures();
  Serial.print("Temp: ");
  Serial.println(ds18sensors.getTempCByIndex(0));

  int rainVal = analogRead(RAIN_PIN);
  Serial.print("Rain: "); Serial.println(rainVal);
   
  Serial.println("** End loop **");
  Serial.println("");
  
  delay(2000);
  digitalWrite(13, LOW);
  delay(2000);

}

/* sample output:
*****************************
** Start loop **
== tsl2561 ========
TSLlux: 252
== si1145 =======
SIvis: 265
SIir: 275
SIuv: 0.04
== Guva   =======
Guva mV: 0.00
Guva: 0.00
== UV6075 =======
VEMLuva: 22.46
VEMLuvb: 18.35
VEMLuvi: 0.04
Temp: 13.00
== Rain ===========
Rain: 1023
** End loop **
 
*/


