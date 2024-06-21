#include <Wire.h>
#include <LiquidCrystal.h>
#include <WiFi.h>
#include <I2C_RTC.h>
#include <WiFiManager.h>
#include <time.h>

#include "config.h"
#include "ProgressBar.h"

// Pin definitions for Arduino Nano ESP32
constexpr int SDA_PIN = A6;
constexpr int SCL_PIN = A7;

constexpr int BUTTON_25_MIN_PIN = A0; // button 1
constexpr int BUTTON_5_MIN_PIN = A1; // button 2
constexpr int BUTTON_15_MIN_PIN = A2; // button 3
constexpr int BUTTON_CLOCK_PIN = A3; // button 4

constexpr int BUZZER_PIN = D10;

// LCD pin definitions
constexpr int LCD_RS_PIN = D9 ;
constexpr int LCD_ENABLE_PIN = D8;
constexpr int LCD_D4_PIN = D7;
constexpr int LCD_D5_PIN = D6;
constexpr int LCD_D6_PIN = D5;
constexpr int LCD_D7_PIN = D2;

// LCD dimensions
constexpr int LCD_COLUMNS = 16;
constexpr int LCD_LINES = 2;

// Initialize LCD display
LiquidCrystal lcd(LCD_RS_PIN, LCD_ENABLE_PIN, LCD_D4_PIN, LCD_D5_PIN, LCD_D6_PIN, LCD_D7_PIN);
ProgressBar pb(lcd, LCD_COLUMNS, 1);

// Initialize RTC
constexpr char* timezone = "CET-1CEST,M3.5.0,M10.5.0/3";
static DS1307 RTC;

// Global variables for countdown management
unsigned long countdownMillis;
unsigned long lastCountdownDuration;
bool isCountdownActive = false;

// Function declarations
String wifiStatusToString(wl_status_t status);
String dayOfWeekToString(int dayOfWeek);
void copyRTCToLocalTime();
void updateRTCFromNTP();
void startCountdown(unsigned long durationMillis);
void displayTime();
void displayCountdown();
void triggerBuzzer();
void setupWiFi();
void configureNTP();
void setupPins();
void IRAM_ATTR handleButtonPress();
void createCustomCharacters();

void setup() {
  setupPins();

  // Start serial communication
  Serial.begin(115200);

  // Initialize LCD display
  lcd.begin(LCD_COLUMNS, LCD_LINES);
  lcd.clear();
  pb.begin();

  // Initialize RTC
  Wire.setPins(SDA_PIN, SCL_PIN);
  RTC.begin();

  // copyRTCToLocalTime();

  // Setup WiFi and NTP
  setupWiFi();
  configureNTP();
}

void loop() {
  if (isCountdownActive) {
    displayCountdown();
  } else {
    displayTime();
  }

  delay(50);
}

// Convert WiFi status to a string
String wifiStatusToString(wl_status_t status) {
  switch (status) {
    case WL_IDLE_STATUS: return "Idle";
    case WL_NO_SSID_AVAIL: return "No SSID";
    case WL_SCAN_COMPLETED: return "Scan Done";
    case WL_CONNECTED: return "Connected";
    case WL_CONNECT_FAILED: return "Connect Fail";
    case WL_CONNECTION_LOST: return "Conn Lost";
    case WL_DISCONNECTED: return "Disconnected";
    default: return "Unknown";
  }
}

// Convert day of the week to string in Italian
String dayOfWeekToString(int dayOfWeek) {
  switch (dayOfWeek) {
    case 0: return "DOM";
    case 1: return "LUN";
    case 2: return "MAR";
    case 3: return "MER";
    case 4: return "GIO";
    case 5: return "VEN";
    case 6: return "SAB";
    default: return "???";
  }
}

// Copy RTC time to local time
void copyRTCToLocalTime() {
  struct tm tm;

  tm.tm_year = RTC.getYear() - 1900;  // RTC year is 2000-based, tm year is 1900-based
  tm.tm_mon = RTC.getMonth() - 1;     // RTC month is 1-based, tm month is 0-based
  tm.tm_mday = RTC.getDay();
  tm.tm_hour = RTC.getHours();
  tm.tm_min = RTC.getMinutes();
  tm.tm_sec = RTC.getSeconds();
  tm.tm_isdst = -1;                   // Automatically determine whether DST is in effect

  time_t t = mktime(&tm);
  struct timeval tv = { .tv_sec = t, .tv_usec = 0 };

  // Imposta la timezone a Europe/Berlin
  setenv("TZ", timezone, 1);
  tzset();

  settimeofday(&tv, NULL);

  Serial.println("RTC time copied to local time");
}

// Update RTC using NTP time
void updateRTCFromNTP() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Failed to obtain");
    lcd.setCursor(0, 1);
    lcd.print("time from NTP");
    delay(2000);
    return;
  }

  RTC.setDate(timeinfo.tm_mday, timeinfo.tm_mon + 1, timeinfo.tm_year + 1900);  // Set date
  RTC.setTime(timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);              // Set time
  RTC.updateWeek();

  Serial.println("Time obtained");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("RTC Updated");
  delay(2000);
}

// Start countdown timer
void startCountdown(unsigned long durationMillis) {
  countdownMillis = millis() + durationMillis;
  lastCountdownDuration = durationMillis;
  isCountdownActive = true;
}

// Display current time
void displayTime() {
  lcd.setCursor(0, 0);
  lcd.printf(" %s %02d/%02d/%04d ", dayOfWeekToString(RTC.getWeek()).c_str(), RTC.getDay(), RTC.getMonth(), RTC.getYear());
  lcd.setCursor(0, 1);
  lcd.printf("    %02d:%02d:%02d    ", RTC.getHours(), RTC.getMinutes(), RTC.getSeconds());
}

// Display countdown timer with vertical progress bar
void displayCountdown() {
  unsigned long currentMillis = millis();
  if (currentMillis >= countdownMillis) {
    isCountdownActive = false;
    triggerBuzzer();
    displayTime();
    return;
  }
  double remainingMillis = countdownMillis - currentMillis;
  unsigned long remainingSeconds = (unsigned long)round(remainingMillis / 1000.0);
  unsigned long minutes = remainingSeconds / 60;
  unsigned long seconds = remainingSeconds % 60;

  lcd.setCursor(0, 0);
  lcd.printf("Countdown: %02lu:%02lu ", minutes, seconds);

  pb.displayProgress(remainingMillis / lastCountdownDuration);
}

// Trigger buzzer with a "tadadada" sound pattern four times
void triggerBuzzer() {
  constexpr int buzzerDuration = 80;
  constexpr int buzzerPause = 200;

  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      digitalWrite(BUZZER_PIN, HIGH);
      delay(buzzerDuration);
      digitalWrite(BUZZER_PIN, LOW);
      delay(buzzerDuration);
    }
    delay(buzzerPause);
  }
}

// Setup WiFi
void setupWiFi() {
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");
  WiFiManager wifiManager;
  wifiManager.setConnectTimeout(30);

  if (!wifiManager.autoConnect(ssid, password)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Failed");
    Serial.println("Failed to connect to WiFi");
    lcd.setCursor(0, 1);
    lcd.print("Retrying...");
    delay(5000);    // Wait for 5 seconds before retrying
    ESP.restart();  // Restart the ESP32 to retry WiFi connection
  }

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connected");
  lcd.setCursor(0, 1);
  lcd.print(WiFi.localIP().toString().c_str());

  Serial.println("WiFi Connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  delay(2000);
}

// Configure NTP time
void configureNTP() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Updating time...");

  // Configura il fuso orario per l'Europa/Berlino
  configTzTime(timezone, "europe.pool.ntp.org");
  updateRTCFromNTP();
}

// Setup pins for buttons and buzzer
void setupPins() {
  // Configure pins for buttons
  pinMode(BUTTON_15_MIN_PIN, INPUT_PULLDOWN);
  pinMode(BUTTON_CLOCK_PIN, INPUT_PULLDOWN);
  pinMode(BUTTON_5_MIN_PIN, INPUT_PULLDOWN);
  pinMode(BUTTON_25_MIN_PIN, INPUT_PULLDOWN);

  // Configure buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // Attach interrupts to the buttons
  attachInterrupt(digitalPinToInterrupt(BUTTON_25_MIN_PIN), handleButtonPress, RISING);
  attachInterrupt(digitalPinToInterrupt(BUTTON_5_MIN_PIN), handleButtonPress, RISING);
  attachInterrupt(digitalPinToInterrupt(BUTTON_15_MIN_PIN), handleButtonPress, RISING);
  attachInterrupt(digitalPinToInterrupt(BUTTON_CLOCK_PIN), handleButtonPress, RISING);
}

// Handle button presses using interrupts
void IRAM_ATTR handleButtonPress() {
  if (digitalRead(BUTTON_25_MIN_PIN) == HIGH) {
    startCountdown(25 * 60 * 1000);  // 25 minutes
  } else if (digitalRead(BUTTON_5_MIN_PIN) == HIGH) {
    startCountdown(5 * 60 * 1000);  // 5 minutes
  } else if (digitalRead(BUTTON_15_MIN_PIN) == HIGH) {
    startCountdown(15 * 60 * 1000);  // 15 minutes
  } else if (digitalRead(BUTTON_CLOCK_PIN) == HIGH) {
    isCountdownActive = false;  // Return to clock
  }
}
