#include "HX711.h"
#include <SPI.h>
#include <WiFi.h>
#include <HTTPClient.h>

HX711 scale;
int weight;
const char *ssid = "test";
const char *passw = "123456789";
#define host "10.64.64.190"
#define port 4000

uint8_t dataPin = 22;
uint8_t clockPin = 23;

int numbers[50]; 

void setup()
{
  Serial.begin(115200);
  Serial.println(__FILE__);
  Serial.print("LIBRARY VERSION: ");
  Serial.println(HX711_LIB_VERSION);
  Serial.println();
  
  WiFi.begin(ssid, passw);
  Serial.print("WiFi connecting..");
  while ((WiFi.status() != WL_CONNECTED)) {
    delay(200);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected !");
    sayHi();
  } else {
    Serial.println("Disconnected !");
  }
  
  SPI.begin(); // init SPI bus


  scale.begin(dataPin, clockPin);

  // TODO find a nice solution for this calibration..
  // load cell factor 20 KG
  // scale.set_scale(127.15);

  // load cell factor 5 KG      
  scale.set_scale(-63.834618);
  // reset the scale to zero = 0
  scale.tare(20);
}

//Serial.println(scale.get_units(1));

void loop()
{
    String uuid = "62481b51";
    if (scale.is_ready())
    {
        for (int i = 0; i < 50; i++)
        {
            weight = scale.get_units(1);
            numbers[i] = weight;
            Serial.println(weight);
            
        }

        // Sort the numbers array
        for (int i = 0; i < 50 - 1; i++)
        {
            for (int j = 0; j < 50 - i - 1; j++)
            {
                if (numbers[j] > numbers[j + 1])
                {
                    int temp = numbers[j];
                    numbers[j] = numbers[j + 1];
                    numbers[j + 1] = temp;
                }
            }
        }

        // Calculate median
        float median;
        if (50 % 2 == 0)
        {
            median = (numbers[50 / 2 - 1] + numbers[50 / 2]) / 2.0;
        }
        else
        {
            median = numbers[50 / 2];
        }

        Serial.print("Median: ");
        Serial.println(int(median));
        if(median <= 200){
          Serial.println("Weight is not correct");
        }
        else{
          WriteRFID(String(median), uuid);
        }
    }
}



void sayHi() {
  WiFiClient client;
  HTTPClient http;
  if (http.begin(client, "http://" + String(host) + ":" + String(port) + "/")) {
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      String payload = http.getString();
      Serial.println(payload);
    } else {
      Serial.print("HTTP Request failed. Error code: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("Failed to connect to the server");
  }
}



String _weight; 
String _uuid;
void WriteRFID(String weight, String uuid) {
  _weight = weight;
  _uuid = uuid;
  WiFiClient client;
  HTTPClient http;
  if (http.begin(client, "http://" + String(host) + ":" + String(port) + "/writeweight/" + _weight + "/" + _uuid)) {
    int httpResponseCode = http.POST(String());

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      String payload = http.getString();
      Serial.println(payload);
    } else {
      Serial.print("HTTP Request failed. Error code: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("Failed to connect to the server");
  }
}
