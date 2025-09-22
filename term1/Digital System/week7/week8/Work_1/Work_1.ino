// กำหนดขาที่ต่อ LED
int ledPins[] = {13, 12, 11};  
int ledCount = 3; // จำนวน LED

void setup() {
  // ตั้งค่า pin ทั้งหมดเป็น OUTPUT
  for (int i = 0; i < ledCount; i++) {
    pinMode(ledPins[i], OUTPUT);
  }
}

void loop() {
  // วนให้ LED ติดทีละดวง
  for (int i = 0; i < ledCount; i++) {
    digitalWrite(ledPins[i], HIGH); // ติด
    delay(200);                     // รอ 0.5 วินาที
    digitalWrite(ledPins[i], LOW);  // ดับ
    delay(200);                     // รอ 0.5 วินาที
  }
}
