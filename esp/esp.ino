#include <WiFi.h>
#include <HTTPClient.h>
#include <ModbusMaster.h>
#include <DHT.h>

// ---------------- USER CONFIG ----------------
const char* WIFI_SSID     = "Pixel";
const char* WIFI_PASSWORD = "12341234";
const char* SERVER_HOST   = "10.231.48.1"; // Flask server IP
const uint16_t SERVER_PORT = 5000;
const char* SENSOR_API_PATH = "/sensor";

// ---------------- HARDWARE ----------------
#define MAX485_EN   25
#define RXD2        16
#define TXD2        17
#define DHTPIN      4
#define DHTTYPE     DHT22

#define PH_PIN      35 // pH analog (ADC1)

// ---------------- GLOBALS ----------------
ModbusMaster node;
DHT dht(DHTPIN, DHTTYPE);
const float PH_VREF  = 3.3f;
const int   PH_BITS  = 4095;
float PH_SLOPE  = -4.90f;
float PH_OFFSET = 15.00f;

// ---------------- HELPERS ----------------
void rs485PreTx()  { digitalWrite(MAX485_EN, HIGH); }
void rs485PostTx() { digitalWrite(MAX485_EN, LOW); }

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected! IP: " + WiFi.localIP().toString());
}

float readPhVoltage(uint8_t samples = 10, uint16_t delayMs = 30) {
  int buf[10];
  if (samples > 10) samples = 10;
  for (uint8_t i = 0; i < samples; i++) buf[i] = analogRead(PH_PIN), delay(delayMs);
  // sort ascending
  for (uint8_t i = 0; i < samples - 1; i++)
    for (uint8_t j = i + 1; j < samples; j++)
      if (buf[i] > buf[j]) { int t = buf[i]; buf[i] = buf[j]; buf[j] = t; }
  uint8_t start = (samples >= 6) ? 2 : 0;
  uint8_t end   = (samples >= 6) ? (samples - 2) : samples;
  uint32_t acc = 0;
  for (uint8_t i = start; i < end; i++) acc += buf[i];
  float avgCounts = float(acc) / float(end - start);
  return avgCounts * PH_VREF / PH_BITS;
}

String buildUrl() {
  return String("http://") + SERVER_HOST + ":" + String(SERVER_PORT) + SENSOR_API_PATH;
}

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);
  pinMode(MAX485_EN, OUTPUT);
  digitalWrite(MAX485_EN, LOW);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  node.begin(1, Serial2);
  node.preTransmission(rs485PreTx);
  node.postTransmission(rs485PostTx);
  dht.begin();
  analogSetPinAttenuation(PH_PIN, ADC_11db);
  connectWiFi();
}

// ---------------- LOOP ----------------
unsigned long lastPost = 0;
const unsigned long POST_PERIOD_MS = 5000;

void loop() {
  if (millis() - lastPost < POST_PERIOD_MS) { delay(50); return; }
  lastPost = millis();

  if (WiFi.status() != WL_CONNECTED) { connectWiFi(); if (WiFi.status() != WL_CONNECTED) return; }

  // Read NPK via Modbus
  uint16_t N=0, P=0, K=0;
  if (node.readHoldingRegisters(0x001E, 3) == node.ku8MBSuccess) {
    N = node.getResponseBuffer(0);
    P = node.getResponseBuffer(1);
    K = node.getResponseBuffer(2);
  }

  // Read DHT22
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Read pH
  float phVolt = readPhVoltage();
  float pH = PH_SLOPE * phVolt + PH_OFFSET;

  // Build JSON
  String json = "{";
  json += "\"N\":" + String(N) + ",";
  json += "\"P\":" + String(P) + ",";
  json += "\"K\":" + String(K) + ",";
  json += "\"temperature\":" + String(isnan(temperature)?0.0:temperature,2) + ",";
  json += "\"humidity\":" + String(isnan(humidity)?0.0:humidity,2) + ",";
  json += "\"ph\":" + String(pH,2) + ",";
  json += "\"rainfall\":0"; // placeholder if no rainfall sensor
  json += "}";

  Serial.println("POST JSON: " + json);

  // Send HTTP POST
  HTTPClient http;
  http.begin(buildUrl());
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(json);
  if (code > 0) Serial.printf("HTTP %d | %s\n", code, http.getString().c_str());
  else Serial.printf("HTTP POST failed: %s (%d)\n", http.errorToString(code).c_str(), code);
  http.end();
}
