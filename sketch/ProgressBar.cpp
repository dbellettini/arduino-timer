#include "Arduino.h"
#include "ProgressBar.h"

ProgressBar::ProgressBar(LiquidCrystal& lcd, uint8_t cols, uint8_t row) 
  : lcd(lcd), cols(cols), row(row) {
}

void ProgressBar::begin() {
  createCustomCharacters();
}

void ProgressBar::createCustomCharacters() {
  for (int i = 0; i < 6; i++) {
    uint8_t block[8];
    uint8_t pattern = createBlockPattern(i);
    for (int j = 0; j < 8; j++) {
      block[j] = pattern;
    }
    lcd.createChar(i, block);
  }
}

uint8_t ProgressBar::createBlockPattern(int filledBits) {
  return 0b11111 << (5 - filledBits);
}

void ProgressBar::displayProgress(double progressRate) {
  int totalBlocks = cols * 5;
  int progress = static_cast<int>(round(totalBlocks * progressRate));

  for (int i = 0; i < cols; i++) {
    int size = min(progress, 5);
    lcd.setCursor(i, row);
    lcd.write(static_cast<uint8_t>(size));
    progress -= size;
  }
}