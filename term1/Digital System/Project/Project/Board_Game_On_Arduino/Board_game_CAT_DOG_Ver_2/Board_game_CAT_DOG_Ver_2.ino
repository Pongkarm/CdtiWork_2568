//หน้าจอหมา 2
//หน้าจอแมว 0
//ปุ่มหมา 17
//ปุ่มแมว 19
//หน้าจอกลาง 1
//ปุ่มกลาง 18
/// ====== ESP32 + TCA9548A + 3 OLED + 3 Buttons + Touch ======
// CH0: SSD1306 128x64 → CAT HUD (ตัวเล็ก, แสดงชื่อ/Pos/Dir + หัวใจมุมขวาบน)
// CH1: SH1106  128x64 → CENTER STATUS (Title, Turn, Pos/Dir ของทั้งสองฝั่ง, Event)
// CH2: SSD1306 128x64 → DOG HUD (ตัวเล็ก, แสดงชื่อ/Pos/Dir + หัวใจมุมขวาบน)
//
// BTN1=GPIO17 → DOG change dir (ทีละคลิก)
// BTN2=GPIO18 → Confirm + Touch roll steps (ทั้งสองฝั่งใช้ปุ่มเดียวกัน)
// BTN3=GPIO19 → CAT change dir
// TOUCH_PIN=GPIO4 (T0): ใช้สุ่มก้าว (sum % 4) + 1
//
// NOTE:
// - หัวใจไม่ได้ใช้บิตแมปแล้ว แต่ “วาด” ด้วยวงกลม+สามเหลี่ยม → ไม่กลับด้านอีก
// - Map แสดงเฉพาะใน Serial Monitor
// - CENTER จะแสดงทุกเหตุการณ์สำคัญ (ทอยได้กี่ก้าว, ชนกำแพง, โจมตี, จบเกม)

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_SH110X.h>

// ---------- I2C & TCA ----------
#define SDA_PIN 21
#define SCL_PIN 22
#define TCA_ADDR 0x70
static inline void tcaSelect(uint8_t ch){ Wire.beginTransmission(TCA_ADDR); Wire.write(1<<ch); Wire.endTransmission(); }

// ---------- channels ----------
#define CAT_CH  0  // SSD1306
#define CTR_CH  1  // SH1106
#define DOG_CH  2  // SSD1306

// ---------- OLED instances ----------
#define SCREEN_W 128
#define SCREEN_H 64
Adafruit_SSD1306  dspCat(SCREEN_W, SCREEN_H, &Wire, -1);
Adafruit_SH1106G  dspCtr(SCREEN_W, SCREEN_H, &Wire, -1);
Adafruit_SSD1306  dspDog(SCREEN_W, SCREEN_H, &Wire, -1);

// ---------- Buttons & Touch ----------
#define BTN1 17
#define BTN2 18
#define BTN3 19
#define TOUCH_PIN 4

// ---------- Board / Rules ----------
const int ROWS=7, COLS=20;
const char EMPTY='.', WALL='#', CAT='C', DOG='D', GOAL='G';

// ← → ↑ ↓
const int8_t dx[4]={0,0,-1,1};
const int8_t dy[4]={-1,1,0,0};
const char* dStr[4]={"LEFT","RIGHT","UP","DOWN"};
const char  dArrow[4]={'<','>','^','v'};

char base_map[ROWS][COLS];

int catX=0, catY=0;
int dogX=6, dogY=0;
int goalX=6, goalY=19;

// HP ของแมว แบบครึ่งหลอด: 2=1.0, 1=0.5, 0=ตาย
int catHP2=2;
bool gameOver=false;

int dirCat=0, dirDog=0;
enum Turn { CAT_TURN=0, DOG_TURN=1 };
Turn turnNow = CAT_TURN;

// ---------- latch button ----------
bool latchBtn1=false, latchBtn2=false, latchBtn3=false;
const uint32_t DEBOUNCE_MS=60;
uint32_t lastEdge1=0, lastEdge2=0, lastEdge3=0;
static inline bool pressedOnce(int pin, bool &latch, uint32_t &lastEdge){
  uint32_t now=millis();
  int lvl = digitalRead(pin);
  if (lvl==LOW && !latch && (now-lastEdge)>DEBOUNCE_MS){ latch=true; lastEdge=now; return true; }
  else if (lvl==HIGH && latch){ latch=false; }
  return false;
}

// =====================================================
// HEART (vector draw, ไม่กลับด้านแน่นอน)
// =====================================================
// วาดหัวใจขนาด ~14x12 ที่มุมขวาบน (xRight,yTop)
// hp2: 2=เต็ม, 1=ครึ่ง (ลบครึ่งขวา), 0=แตก
static void drawHeartTopRight(Adafruit_GFX &dsp, int hp2){
  const int w=14, h=12;
  const int x = dsp.width() - w - 1;
  const int y = 0;
  // ล้างพื้นหลังบริเวณหัวใจ
  dsp.fillRect(x-1,y-1,w+2,h+2,BLACK);

  // วาดหัวใจเต็มด้วย 2 วงกลม + สามเหลี่ยม
  // จุดอ้างอิง (ซ้าย,ขวา) ของกลีบ
  int cxL=x+4, cy=y+4, r=4;
  int cxR=x+9, cy2=y+4;

  // base heart (เต็ม)
  dsp.fillCircle(cxL, cy, r, WHITE);
  dsp.fillCircle(cxR, cy2, r, WHITE);
  // สามเหลี่ยมลงล่าง
  int x1=x, y1=y+5;
  int x2=x+w-1, y2=y+5;
  int xb=x+w/2, yb=y+h-1;
  dsp.fillTriangle(x1,y1, x2,y2, xb,yb, WHITE);

  if (hp2==1){
    // ปิดครึ่งขวาออก (ให้เหลือครึ่งซ้าย → ไม่กลับด้าน)
    dsp.fillRect(x + w/2, y-1, w/2+2, h+2, BLACK);
  } else if (hp2==0){
    // หัวใจแตก: วาดซ้ำแบบเต็ม แล้วขีดรอยแตกทแยง + ตัดร่อง
    dsp.drawLine(x+2, y+2, x+w-3, y+h-3, BLACK);
    dsp.drawLine(x+3, y+2, x+w-4, y+h-4, BLACK);
    // เจาะร่องแตก
    dsp.fillTriangle(x+6,y+4,  x+8,y+7,  x+6,y+9, BLACK);
  }
}

// =====================================================
// SERIAL MAP
// =====================================================
static inline bool in_bounds(int r,int c){ return r>=0 && r<ROWS && c>=0 && c<COLS; }

static void clear_map(){ for(int i=0;i<ROWS;i++) for(int j=0;j<COLS;j++) base_map[i][j]=EMPTY; }

static void build_simple_randomish_map(){
  clear_map();
  for(int i=0;i<ROWS;i++){
    for(int j=0;j<COLS;j++){
      if (random(100) < 12){
        if ((i==catX&&j==catY)||(i==dogX&&j==dogY)||(i==goalX&&j==goalY)) continue;
        base_map[i][j]=WALL;
      }
    }
  }
  // สายล่างพอย์ไปทางขวาให้โล่งบ้าง (ช่วยเดินถึงเป้าหมาย)
  for (int j=0;j<COLS;j++) base_map[goalX][j]= (j==goalY? EMPTY: base_map[goalX][j]);
}

static void printMapToSerial(){
  Serial.println("---- Game Board ----");
  for(int i=0;i<ROWS;i++){
    for(int j=0;j<COLS;j++){
      char ch=base_map[i][j];
      if (i==catX && j==catY) ch=CAT;
      else if (i==dogX && j==dogY) ch=DOG;
      else if (i==goalX && j==goalY) ch=GOAL;
      Serial.print(ch); Serial.print(' ');
    }
    Serial.println();
  }
  Serial.print("CAT("); Serial.print(catX); Serial.print(','); Serial.print(catY); Serial.print(")  ");
  Serial.print("DOG("); Serial.print(dogX); Serial.print(','); Serial.print(dogY); Serial.print(")  ");
  Serial.print("HP=");  Serial.print(catHP2/2); if (catHP2%2) Serial.print(".5");
  Serial.print("  TURN="); Serial.println(turnNow==CAT_TURN? "CAT":"DOG");
}

// =====================================================
// CENTER SCREEN (เยอะขึ้นตามคำขอ)
// =====================================================
static void ctrPrintSmall(int16_t x, int16_t y, const char* s){
  dspCtr.setFont();            // default bitmap font
  dspCtr.setTextSize(1);       // เล็ก อ่านง่าย
  dspCtr.setTextColor(SH110X_WHITE);
  dspCtr.setCursor(x,y);
  dspCtr.print(s);
}

// =====================================================
// CENTER SCREEN (เล็กลง เหลือแค่ TURN + Event)
// =====================================================
static void showCenterStatus(const char* title, const char* msg1="", const char* msg2=""){
  tcaSelect(CTR_CH);
  dspCtr.clearDisplay();

  // Title (เล็กกว่าของเดิม)
  dspCtr.setFont();
  dspCtr.setTextSize(1);    // ขนาดเล็กลง
  dspCtr.setTextColor(SH110X_WHITE);
  dspCtr.setCursor(20, 20);
  dspCtr.print(title);

  // Event (ถ้ามี)
  if (msg1[0]) {
    dspCtr.setCursor(20, 40);
    dspCtr.print(msg1);
  }
  if (msg2[0]) {
    dspCtr.setCursor(20, 52);
    dspCtr.print(msg2);
  }

  dspCtr.display();
}

static void showCenterEvent(const char* title, const char* sub1="", const char* sub2=""){
  showCenterStatus(title, sub1, sub2);
}

// =====================================================
// HUD (เล็กลงอีกนิดตามคำขอ)
// =====================================================
static inline void drawHudCat(){
  tcaSelect(CAT_CH);
  dspCat.clearDisplay();
  dspCat.setFont();          // default bitmap font (เล็ก)
  dspCat.setTextSize(1);
  dspCat.setTextColor(WHITE);

  char line[32];
  dspCat.setCursor(0,10); snprintf(line,sizeof(line),"CAT  Pos(%d,%d)", catX,catY); dspCat.print(line);
  dspCat.setCursor(0,24); snprintf(line,sizeof(line),"Dir: %c %s", dArrow[dirCat], dStr[dirCat]); dspCat.print(line);

  // หัวใจมุมขวาบน
  drawHeartTopRight(dspCat, catHP2);

  dspCat.display();
}

static inline void drawHudDog(){
  tcaSelect(DOG_CH);
  dspDog.clearDisplay();
  dspDog.setFont();
  dspDog.setTextSize(1);
  dspDog.setTextColor(WHITE);

  char line[32];
  dspDog.setCursor(0,10); snprintf(line,sizeof(line),"DOG  Pos(%d,%d)", dogX,dogY); dspDog.print(line);
  dspDog.setCursor(0,24); snprintf(line,sizeof(line),"Dir: %c %s", dArrow[dirDog], dStr[dirDog]); dspDog.print(line);

  drawHeartTopRight(dspDog, catHP2);

  dspDog.display();
}

// =====================================================
// RULES & TURNS
// =====================================================
static int rollStepsByTouch(){
  // แตะค้าง→รวมค่า, ปล่อย→สรุป
  while (touchRead(TOUCH_PIN) > 30) { delay(2); }
  uint32_t sum=0, cnt=0;
  while (touchRead(TOUCH_PIN) <= 30){
    sum += (uint32_t)touchRead(TOUCH_PIN);
    cnt++; delay(2);
  }
  if (cnt==0) cnt=1;
  uint32_t mix = sum ^ (micros() & 0xFFFF) ^ esp_random();
  return (int)((mix % 4) + 1);
}

static void apply_cat_damage_half(int half){
  if (gameOver || half<=0) return;
  catHP2 -= half; if (catHP2<0) catHP2=0;
  drawHudCat(); drawHudDog();
  showCenterEvent("DOG ATTACK", "CAT -HP", (half==2? "-1.0":"-0.5"));
  printMapToSerial();
  if (catHP2==0){
    gameOver=true;
    showCenterEvent("DOG WINS!", "", "");
  }
}

static bool is_valid_cat(int x,int y){
  if (!in_bounds(x,y)) return false;
  if (base_map[x][y]==WALL)   return false;
  return true;
}
static bool is_valid_dog(int x,int y){
  if (!in_bounds(x,y)) return false;
  if (base_map[x][y]==WALL)   return false;
  if (x==goalX && y==goalY)   return false;
  return true;
}

static bool check_cat_win(){
  if (catX==goalX && catY==goalY){
    showCenterEvent("CAT WINS!", "", "");
    gameOver=true; return true;
  }
  return false;
}

static void run_cat_turn(){
  showCenterStatus("CAT TURN", "Touch to roll", "");
  int steps = rollStepsByTouch();

  char s1[16]; snprintf(s1,sizeof(s1),"STEP %d", steps);
  showCenterEvent("CAT ROLL", s1, "");
  delay(1200);

  bool blocked=false;
  for(int k=0;k<steps;k++){
    int nx=catX+dx[dirCat], ny=catY+dy[dirCat];
    if (!is_valid_cat(nx,ny)){ blocked=true; break; }
    catX=nx; catY=ny;
    // ถ้าทับหมาระหว่างทาง โดน -1.0 ทันที (เกมจบได้)
    if (catX==dogX && catY==dogY){ apply_cat_damage_half(2); if (gameOver) return; }
  }
  if (blocked){
    showCenterEvent("CAT BLOCKED", "WALL!", "");
    delay(1000);
  }
  printMapToSerial();
  drawHudCat(); drawHudDog();
  check_cat_win();
}

static void run_dog_turn(){
  showCenterStatus("DOG TURN", "Touch to roll", "");
  int steps = rollStepsByTouch();

  char s1[16]; snprintf(s1,sizeof(s1),"STEP %d", steps);
  showCenterEvent("DOG ROLL", s1, "");
  delay(1200);

  bool touched=false, blocked=false;
  for(int k=0;k<steps;k++){
    int nx=dogX+dx[dirDog], ny=dogY+dy[dirDog];
    if (!is_valid_dog(nx,ny)){ blocked=true; break; }
    dogX=nx; dogY=ny;
    if (dogX==catX && dogY==catY) touched=true;
  }
  if (blocked){
    showCenterEvent("DOG BLOCKED", "WALL!", "");
    delay(1000);
  }
  printMapToSerial();
  drawHudCat(); drawHudDog();

  // ดาเมจตามกติกา
  if (dogX==catX && dogY==catY)            apply_cat_damage_half(2); // จบเทิร์นทับ → -1.0
  else if (touched && !gameOver)            apply_cat_damage_half(1); // แค่เดินผ่าน → -0.5
}

// =====================================================
// setup / loop
// =====================================================
void setup(){
  Serial.begin(115200);
  Wire.begin(SDA_PIN,SCL_PIN);
  Wire.setClock(400000);
  randomSeed(esp_random());

  pinMode(BTN1,INPUT_PULLUP);
  pinMode(BTN2,INPUT_PULLUP);
  pinMode(BTN3,INPUT_PULLUP);

  // init displays
  tcaSelect(CAT_CH); if (!dspCat.begin(SSD1306_SWITCHCAPVCC,0x3C)) { Serial.println("CAT OLED init fail"); }
  tcaSelect(CTR_CH); if (!dspCtr.begin(0x3C,true))                 { Serial.println("CENTER OLED init fail"); }
  tcaSelect(DOG_CH); if (!dspDog.begin(SSD1306_SWITCHCAPVCC,0x3C)) { Serial.println("DOG OLED init fail"); }

  build_simple_randomish_map();
  printMapToSerial();

  // UI แรกเข้า
  showCenterStatus("READY", "Press BTN2", "");
  drawHudCat();
  drawHudDog();
}

void loop(){
  if (gameOver) return;

  if (turnNow==CAT_TURN){
    if (pressedOnce(BTN3,latchBtn3,lastEdge3)){ dirCat=(dirCat+1)%4; drawHudCat(); showCenterStatus("CAT TURN","Dir changed",""); }
    if (pressedOnce(BTN2,latchBtn2,lastEdge2)){ run_cat_turn(); if (!gameOver){ turnNow=DOG_TURN; showCenterStatus("DOG TURN","",""); } }
  } else {
    if (pressedOnce(BTN1,latchBtn1,lastEdge1)){ dirDog=(dirDog+1)%4; drawHudDog(); showCenterStatus("DOG TURN","Dir changed",""); }
    if (pressedOnce(BTN2,latchBtn2,lastEdge2)){ run_dog_turn(); if (!gameOver){ turnNow=CAT_TURN; showCenterStatus("CAT TURN","",""); } }
  }

  delay(5);
}
