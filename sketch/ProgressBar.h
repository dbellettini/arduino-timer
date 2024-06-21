#ifndef PROGRESSBAR_H
#define PROGRESSBAR_H

#include <LiquidCrystal.h>

class ProgressBar {
public:
    ProgressBar(LiquidCrystal& lcd, uint8_t cols, uint8_t row);
    void begin();
    void displayProgress(double progressRate);

private:
    LiquidCrystal& lcd;
    uint8_t cols, row;

    void createCustomCharacters();
    uint8_t createBlockPattern(int filledBits);
};

#endif