#include <Arduino.h>

void setup(void) {
    Serial.begin(9600);
    pinMode(4, OUTPUT);
}


void loop(void) {
    digitalWrite(4, HIGH);    // จ่ายไฟออกที่ขา D4 (เปิด LED)
    delay(100);              // หน่วงเวลา 1000 มิลลิวินาที (1 วินาที)
    digitalWrite(4, LOW);     // ตัดไฟออกที่ขา D4 (ปิด LED)
    delay(100);              // หน่วงเวลาอีก 1 วินาที
}
