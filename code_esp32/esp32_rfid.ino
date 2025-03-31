#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

const char *ssid = "taskger_2.4G";
const char *passw = "123456789";
#define host "192.168.1.107"
#define port 4000

#define SS_PIN  5  // ESP32 pin GIOP5
#define RST_PIN 27 // ESP32 pin GIOP27

MFRC522 rfid(SS_PIN, RST_PIN);

String response;
String _str, _res;


void setup() {
  Serial.begin(115200);
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
  rfid.PCD_Init(); // init MFRC522

  Serial.println("Tap an RFID/NFC tag on the RFID-RC522 reader");
}

void loop() {
  if (rfid.PICC_IsNewCardPresent()) { // new tag is available
    if (rfid.PICC_ReadCardSerial()) { // NUID has been read
      MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
      Serial.print("Type of RFID/NFC: ");
      Serial.println(rfid.PICC_GetTypeName(piccType));

      // Print UID in Serial Monitor in hex format
      Serial.print("UID:");
      String rfidUID = ""; // Variable to store RFID UID as a string
      for (int i = 0; i < rfid.uid.size; i++) {
        Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(rfid.uid.uidByte[i], HEX);        
        rfidUID += String(rfid.uid.uidByte[i], HEX); // Build the RFID UID string
      }
       Serial.println();
        if (rfid.uid.uidByte[0] == 0x62 && rfid.uid.uidByte[1] == 0x48 && rfid.uid.uidByte[2] == 0x1B && rfid.uid.uidByte[3] == 0x51) {
          Serial.println("เครื่อง : Banana 1");
          String id = "Banana1";
          WriteRFID(rfidUID,id);

        } else if (rfid.uid.uidByte[0] == 0x72 && rfid.uid.uidByte[1] == 0x49 && rfid.uid.uidByte[2] == 0x62 && rfid.uid.uidByte[3] == 0x51) { 
          Serial.println("เครื่อง : Banana 2");
          String id = "Banana2";
          WriteRFID(rfidUID,id);

        } else {
          Serial.println("ไม่มีพบข้อมูล card นี้ในระบบ");
          }
        

      rfid.PICC_HaltA(); // halt PICC
      rfid.PCD_StopCrypto1(); // stop encryption on PCD
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

String _uuid; 
String _idesp; 

void WriteRFID(String uuid, String idesp) {
  _uuid = uuid;
  _idesp = idesp;
  WiFiClient client;
  HTTPClient http;
  if (http.begin(client, "http://" + String(host) + ":" + String(port) + "/write/" + _uuid + "/" + _idesp)) {
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

