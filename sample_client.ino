#include <WiFi.h>
#include <WiFiClient.h>
#include <MFRC522.h>
#include <SPI.h>
#include <ArduinoJson.h>

const char* ssid = "WIFI NAME HERE";
const char* password = "PASSWORD HERE";
const char* server_ip = "127.0.0.1"; // Feel free to change this to the corresponding server IP or domain
const uint16_t server_port = 8000; // Feel free to change this to the appropriate port, especially if port-forwarding is involved

#define SS_PIN 5
#define RST_PIN 34
MFRC522 rfid(SS_PIN, RST_PIN);

const String LOCATION_ID = "CDM";
const char* DEDUCTION_MATRIX[][2] = {
  {"EMD", "50"},
  {"NMD", "50"},
  {"SMD", "50"}
};

String rfid_data = "";
bool rfid_data_ready = false;
SemaphoreHandle_t dataSemaphore;

TaskHandle_t readRFIDTaskHandle;
TaskHandle_t sendToServerTaskHandle;

void setup() {
  Serial.begin(115200);
  SPI.begin();       
  Serial.println("Initializing RFID reader...");
  rfid.PCD_Init();    
  Serial.println("RFID reader initialized");

  dataSemaphore = xSemaphoreCreateBinary();

  connectToWiFi();

  xTaskCreatePinnedToCore(readRFIDTask, "Read RFID Task", 4096, NULL, 1, &readRFIDTaskHandle, 1);
  xTaskCreatePinnedToCore(sendToServerTask, "Send to Server Task", 4096, NULL, 1, &sendToServerTaskHandle, 0);
}

void loop() {
}

void connectToWiFi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void readRFIDTask(void * parameter) {
  for (;;) {
    if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
      rfid_data = "";
      for (byte i = 0; i < rfid.uid.size; i++) {
        String byteStr = String(rfid.uid.uidByte[i], HEX);
        if (byteStr.length() == 1) byteStr = "0" + byteStr;
        byteStr.toUpperCase();
        rfid_data += byteStr;
      }
      Serial.print("RFID data read: ");
      Serial.println(rfid_data);

      rfid_data_ready = true;
      xSemaphoreGive(dataSemaphore);

      rfid.PICC_HaltA();
    }
  }
}

void sendToServerTask(void * parameter) {
  for (;;) {
    if (xSemaphoreTake(dataSemaphore, portMAX_DELAY) == pdTRUE) {
      if (rfid_data_ready) {
        WiFiClient client;
        if (client.connect(server_ip, server_port)) {
          Serial.println("Connected to server");

          StaticJsonDocument<200> json;
          json["rfid_data"] = rfid_data;
          json["location_id"] = LOCATION_ID;
          JsonObject matrix = json.createNestedObject("deduction_matrix");
          for (int i = 0; i < sizeof(DEDUCTION_MATRIX) / sizeof(DEDUCTION_MATRIX[0]); i++) {
            matrix[DEDUCTION_MATRIX[i][0]] = atoi(DEDUCTION_MATRIX[i][1]);
          }

          String jsonStr;
          serializeJson(json, jsonStr);

          client.println(jsonStr);

          String response = client.readStringUntil('\r');
          Serial.println("Server response: " + response);

          client.stop();
          rfid_data_ready = false;
        } else {
          Serial.println("Connection to server failed");
        }
      }
    }
  }
}
