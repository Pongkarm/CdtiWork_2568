// ====== ESP32 + TCA9548A + 3 OLED + 3 Buttons + Touch ======
// ch1 (TCA:1, SH1106 128x64) → MAP (7x20)  [ไม่มี Turn/HP]
// ch0 (TCA:0, SSD1306 128x64) → CAT HUD (FreeSans9pt + หัวใจบิตแมปมุมขวาบน)
// ch2 (TCA:2, SSD1306 128x64) → DOG HUD (FreeSans9pt + หัวใจบิตแมปมุมขวาบน)
// BTN1=GPIO17 → DOG dir, BTN2=GPIO18 → Confirm+Touch roll, BTN3=GPIO19 → CAT dir
// Touch: T0 GPIO4 → (sum % 4) + 1

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_SH110X.h>
#include <Fonts/FreeSans9pt7b.h>
#include <pgmspace.h>
#include <esp_system.h> // esp_random()

// ---------- I2C & TCA ----------
#define SDA_PIN 21
#define SCL_PIN 22
#define TCA_ADDR 0x70
static inline void tcaSelect(uint8_t ch){ Wire.beginTransmission(TCA_ADDR); Wire.write(1<<ch); Wire.endTransmission(); }

// ---------- channels ----------
#define MAP_CH  1  // SH1106
#define CAT_CH  0  // SSD1306
#define DOG_CH  2  // SSD1306

// ---------- OLED instances ----------
#define SCREEN_W 128
#define SCREEN_H 64
#define SH1106_X_OFFSET 0

Adafruit_SH1106G dspMap(SCREEN_W, SCREEN_H, &Wire, -1);   // MAP (SH1106) on ch1
Adafruit_SSD1306  dspCat(SCREEN_W, SCREEN_H, &Wire, -1);  // CAT HUD on ch0
Adafruit_SSD1306  dspDog(SCREEN_W, SCREEN_H, &Wire, -1);  // DOG HUD on ch2

// ---------- Buttons & Touch ----------
#define BTN1 17  // DOG direction
#define BTN2 18  // confirm + touch roll
#define BTN3 19  // CAT direction
#define TOUCH_PIN 4

// ---------- Board / Rules ----------
const int ROWS=7, COLS=20;
const char EMPTY='.', WALL='#', CAT='C', DOG='D', GOAL='G';

// dir order: ← → ↑ ↓
const int8_t dx[4]={0,0,-1,1};
const int8_t dy[4]={-1,1,0,0};
const char* dStr[4]={"LEFT","RIGHT","UP","DOWN"};
const char  dArrow[4]={'<','>','^','v'};

char base_map[ROWS][COLS];

int catX=0, catY=0;
int dogX=6, dogY=0;
int goalX=6, goalY=19;

// HP หน่วยครึ่งหลอด: 2=1.0, 1=0.5, 0=ตาย
int catHP2=2;
bool gameOver=false;

int dirCat=0, dirDog=0;
enum Turn { CAT_TURN=0, DOG_TURN=1 };
Turn turnNow = CAT_TURN;

// --- input: “กดครั้งเดียว” ไม่มี auto-repeat ---
bool latchBtn1=false, latchBtn2=false, latchBtn3=false;
const uint32_t DEBOUNCE_MS=60;
uint32_t lastEdge1=0, lastEdge2=0, lastEdge3=0;

static inline bool pressedOnce(int pin, bool &latch, uint32_t &lastEdge){
  uint32_t now=millis();
  int lvl = digitalRead(pin); // LOW = กด
  if (lvl==LOW && !latch && (now-lastEdge)>DEBOUNCE_MS){ latch=true; lastEdge=now; return true; }
  else if (lvl==HIGH && latch){ latch=false; }
  return false;
}

// =====================================================
// 1) BITMAP HEARTS (16x16, 1-bit, กลีบซ้าย/ขวาถูกทิศ)
// =====================================================
const uint8_t BM_HEART_FULL_16[] PROGMEM = {
  0x00,0x00,
  0x30,0x0C,
  0x78,0x1E,
  0xFC,0x3F,
  0xFE,0x7F,
  0xFE,0x7F,
  0xFE,0x7F,
  0xFC,0x3F,
  0xF8,0x1F,
  0xF0,0x0F,
  0xE0,0x07,
  0xC0,0x03,
  0x80,0x01,
  0x00,0x00,
  0x00,0x00,
  0x00,0x00,
};

const uint8_t BM_HEART_BROKEN_16[] PROGMEM = {
  0x00,0x00,
  0x30,0x0C,
  0x78,0x1E,
  0xFC,0x3F,
  0xFE,0x7F,
  0xEE,0x6F,
  0xDE,0x77,
  0xBC,0x3B,
  0x78,0x1D,
  0xF0,0x0F,
  0xE0,0x07,
  0xC0,0x03,
  0x80,0x01,
  0x00,0x00,
  0x00,0x00,
  0x00,0x00,
};

// =====================================================
// 2) HEART HELPERS (typedef มาก่อนใช้ทุกครั้ง)
//    ครึ่งหัวใจทำด้วยการ mask ครึ่ง (ซ้าย/ขวาเลือกได้)
// =====================================================
#define HEART_HALF_ON_LEFT  1   // 1=ครึ่งซ้าย, 0=ครึ่งขวา

// =====================================================
// HEART STRUCT + HELPERS
// =====================================================

// ต้องประกาศ struct ก่อนทุกอย่าง
struct HeartBM {
  const uint8_t* p;
  uint8_t w;
  uint8_t h;
};

// prototype ฟังก์ชันก่อน
HeartBM pickFullHeart();
HeartBM pickBrokenHeart();

// implement ฟังก์ชันเลือกหัวใจ
HeartBM pickFullHeart() {
  HeartBM h = { BM_HEART_FULL_16, 16, 16 };
  return h;
}
HeartBM pickBrokenHeart() {
  HeartBM h = { BM_HEART_BROKEN_16, 16, 16 };
  return h;
}


// วาดหัวใจที่มุมขวาบน (SSD1306)
static inline void drawHeartTopRight(Adafruit_SSD1306 &dsp, int hp2) {
  int x = 127 - 16, y = 0;
  if (hp2 >= 2) {
    HeartBM bm = pickFullHeart(); dsp.drawXBitmap(x, y, bm.p, bm.w, bm.h, 1);
  } else if (hp2 == 1) {
    HeartBM bm = pickFullHeart(); dsp.drawXBitmap(x, y, bm.p, bm.w, bm.h, 1);
    if (HEART_HALF_ON_LEFT) dsp.fillRect(x + bm.w/2, y, bm.w/2, bm.h, SSD1306_BLACK);
    else                    dsp.fillRect(x,          y, bm.w/2,  bm.h, SSD1306_BLACK);
  } else {
    HeartBM bm = pickBrokenHeart(); dsp.drawXBitmap(x, y, bm.p, bm.w, bm.h, 1);
  }
}
// วาดหัวใจที่มุมขวาบน (SH1106G)
static inline void drawHeartTopRight(Adafruit_SH1106G &dsp, int hp2) {
  int x = 127 - 16, y = 0;
  if (hp2 >= 2) {
    HeartBM bm = pickFullHeart(); dsp.drawXBitmap(x, y, bm.p, bm.w, bm.h, 1);
  } else if (hp2 == 1) {
    HeartBM bm = pickFullHeart(); dsp.drawXBitmap(x, y, bm.p, bm.w, bm.h, 1);
    if (HEART_HALF_ON_LEFT) dsp.fillRect(x + bm.w/2, y, bm.w/2, bm.h, SH110X_BLACK);
    else                    dsp.fillRect(x,          y, bm.w/2,  bm.h, SH110X_BLACK);
  } else {
    HeartBM bm = pickBrokenHeart(); dsp.drawXBitmap(x, y, bm.p, bm.w, bm.h, 1);
  }
}

// =====================================================
// Traps
// =====================================================
#define MAX_TRAPS 6
#define TRAP_SPIKE_CAT  0   // แมวเหยียบ -> -0.5
#define TRAP_SNARE_DOG  1   // หมาเหยียบ -> หยุดทันที + ข้าม 1 เทิร์น

struct Trap { int r,c; uint8_t type; bool active; };
Trap traps[MAX_TRAPS];
int nTraps = 0;
int dog_skip_turns = 0;   // หมาโดนบ่วง ข้ามกี่เทิร์น

// =====================================================
// utils & map
// =====================================================
bool in_bounds(int r,int c){ return r>=0 && r<ROWS && c>=0 && c<COLS; }
void clear_map(){ for(int i=0;i<ROWS;i++) for(int j=0;j<COLS;j++) base_map[i][j]=EMPTY; }

void build_simple_randomish_map(){
  clear_map();
  for(int i=0;i<ROWS;i++){
    for(int j=0;j<COLS;j++){
      if (random(100) < 12){
        if ((i==catX&&j==catY)||(i==dogX&&j==dogY)||(i==goalX&&j==goalY)) continue;
        base_map[i][j]=WALL;
      }
    }
  }
  for(int j=0;j<COLS;j++) base_map[goalX][j]=EMPTY; // ล่างโล่งถึง GOAL
}

void spawn_traps() {
  for (int i=0;i<MAX_TRAPS;i++) traps[i].active=false;
  nTraps = 0;

  int total = 2 + (int)random(0, MAX_TRAPS-1); // 2..MAX_TRAPS
  if (total > MAX_TRAPS) total = MAX_TRAPS;
  int wantSpike = total/2;
  int wantSnare = total - wantSpike;

  int emptR[ROWS*COLS], emptC[ROWS*COLS], M=0;
  bool used[ROWS][COLS]; memset(used, 0, sizeof(used));
  used[catX][catY]=used[dogX][dogY]=used[goalX][goalY]=true;

  for (int i=0;i<ROWS;i++) for (int j=0;j<COLS;j++){
    if (base_map[i][j]!=WALL && !used[i][j]) { emptR[M]=i; emptC[M]=j; M++; }
  }
  for (int i=M-1;i>0;i--){
    int j=random(0,i+1);
    int tr=emptR[i], tc=emptC[i];
    emptR[i]=emptR[j]; emptC[i]=emptC[j];
    emptR[j]=tr;       emptC[j]=tc;
  }

  int idx=0;
  for (int k=0;k<wantSpike && idx<M; k++){
    traps[nTraps] = { emptR[idx], emptC[idx], TRAP_SPIKE_CAT, true };
    used[emptR[idx]][emptC[idx]] = true;
    nTraps++; idx++;
  }
  for (int k=0;k<wantSnare && idx<M; k++){
    while (idx<M && used[emptR[idx]][emptC[idx]]) idx++;
    if (idx>=M) break;
    traps[nTraps] = { emptR[idx], emptC[idx], TRAP_SNARE_DOG, true };
    used[emptR[idx]][emptC[idx]] = true;
    nTraps++; idx++;
  }
}

// helper: format position
static inline String fmtPos(int r, int c){ String s="("; s+=r; s+=","; s+=c; s+=")"; return s; }

// =====================================================
// draw
// =====================================================
void drawMap(){
  tcaSelect(MAP_CH);
  dspMap.clearDisplay();
  dspMap.setTextSize(1);
  dspMap.setTextColor(SH110X_WHITE);
  dspMap.setFont(); // default bitmap font (5x7)
  for(int i=0;i<ROWS;i++){
    dspMap.setCursor(0+SH1106_X_OFFSET, i*8);
    for(int j=0;j<COLS;j++){
      char ch = base_map[i][j];
      if (i==catX && j==catY) ch=CAT;
      else if (i==dogX && j==dogY) ch=DOG;
      else if (i==goalX && j==goalY) ch=GOAL;
      else {
        for (int t=0;t<nTraps;t++){
          if (traps[t].active && traps[t].r==i && traps[t].c==j){
            ch = (traps[t].type==TRAP_SPIKE_CAT)? '^':'*';
            break;
          }
        }
      }
      dspMap.write(ch); dspMap.write(' ');
    }
  }
  dspMap.display();
}

void drawHudCat(bool showTouchHint=false, int rolledSteps=-1, bool blocked=false){
  tcaSelect(CAT_CH);
  dspCat.clearDisplay();
  dspCat.setTextColor(SSD1306_WHITE);
  dspCat.setFont(&FreeSans9pt7b);

  // บรรทัดบน: ชื่อ + ตำแหน่ง + หัวใจ
  dspCat.setCursor(0,14); dspCat.print("CAT "); dspCat.print(fmtPos(catX,catY));
  drawHeartTopRight(dspCat, catHP2);

  // บรรทัดกลาง: ทิศ
  dspCat.setCursor(0,36);
  dspCat.print("DIR: "); dspCat.print(dArrow[dirCat]); dspCat.print(' '); dspCat.print(dStr[dirCat]);

  // บรรทัดล่าง: สถานะ
  dspCat.setCursor(0,60);
  if (blocked) dspCat.print("BLOCKED");
  else if (rolledSteps>0) { dspCat.print("STEP: "); dspCat.print(rolledSteps); }
  else if (showTouchHint && turnNow==CAT_TURN) dspCat.print("TOUCH to roll...");
  else if (turnNow==CAT_TURN) dspCat.print("Your Turn");

  dspCat.display();
}

void drawHudDog(bool showTouchHint=false, int rolledSteps=-1, bool blocked=false){
  tcaSelect(DOG_CH);
  dspDog.clearDisplay();
  dspDog.setTextColor(SSD1306_WHITE);
  dspDog.setFont(&FreeSans9pt7b);

  dspDog.setCursor(0,14); dspDog.print("DOG "); dspDog.print(fmtPos(dogX,dogY));
  drawHeartTopRight(dspDog, catHP2); // แสดง HP แมว

  dspDog.setCursor(0,36);
  dspDog.print("DIR: "); dspDog.print(dArrow[dirDog]); dspDog.print(' '); dspDog.print(dStr[dirDog]);

  dspDog.setCursor(0,60);
  if (blocked) dspDog.print("BLOCKED");
  else if (rolledSteps>0) { dspDog.print("STEP: "); dspDog.print(rolledSteps); }
  else if (showTouchHint && turnNow==DOG_TURN) dspDog.print("TOUCH to roll...");
  else if (turnNow==DOG_TURN) dspDog.print("Your Turn");

  dspDog.display();
}

// =====================================================
// touch roll
// =====================================================
int rollStepsByTouch(){
  // ปรับ threshold ให้เหมาะกับบอร์ดของคุณ (ลอง Serial.print เพื่อตรวจค่าได้)
  while (touchRead(TOUCH_PIN) > 40) { delay(2); }
  uint32_t sum=0, cnt=0;
  while (touchRead(TOUCH_PIN) <= 40){
    sum += (uint32_t)touchRead(TOUCH_PIN);
    cnt++; delay(2);
  }
  if (cnt==0) cnt=1;
  uint32_t mix = sum ^ (micros() & 0xFFFF) ^ esp_random();
  return (int)((mix % 4) + 1);
}

// =====================================================
// rules & damage
// =====================================================
bool is_valid_move_cat_next(int x,int y){
  if (!in_bounds(x,y)) return false;
  if (base_map[x][y]==WALL) return false;
  return true;
}
bool is_valid_move_dog_next(int x,int y){
  if (!in_bounds(x,y)) return false;
  if (base_map[x][y]==WALL) return false;
  if (x==goalX && y==goalY) return false;
  return true;
}

void apply_cat_damage_half(int half){
  if (gameOver || half<=0) return;
  catHP2 -= half; if (catHP2<0) catHP2=0;
  drawHudCat(); drawHudDog();  // รีเฟรชหัวใจ
  if (catHP2==0){
    gameOver=true;
    delay(600);
    tcaSelect(MAP_CH);
    dspMap.clearDisplay();
    dspMap.setCursor(18+SH1106_X_OFFSET,32);
    dspMap.setTextSize(2);
    dspMap.setFont(); // default
    dspMap.println("DOG WINS!");
    dspMap.display();
  }
}

bool dog_attacks_cat_immediate(){
  if (catX==dogX && catY==dogY){
    apply_cat_damage_half(2); // -1.0
    return true;
  }
  return false;
}
bool check_cat_win(){
  if (catX==goalX && catY==goalY){
    tcaSelect(MAP_CH);
    dspMap.clearDisplay();
    dspMap.setCursor(18+SH1106_X_OFFSET,32);
    dspMap.setTextSize(2);
    dspMap.setFont();
    dspMap.println("CAT WINS!");
    dspMap.display();
    gameOver=true;
    return true;
  }
  return false;
}

// =====================================================
// traps checkers
// =====================================================
void check_cat_trap_here(){
  for (int t=0;t<nTraps;t++){
    if (!traps[t].active) continue;
    if (traps[t].type==TRAP_SPIKE_CAT && traps[t].r==catX && traps[t].c==catY){
      traps[t].active=false;
      drawHudCat(false, -1, false);
      tcaSelect(CAT_CH); dspCat.setCursor(80,60); dspCat.print("TRAP!"); dspCat.display();
      apply_cat_damage_half(1);  // -0.5
      break;
    }
  }
}

bool check_dog_trap_here_and_snare(){
  for (int t=0;t<nTraps;t++){
    if (!traps[t].active) continue;
    if (traps[t].type==TRAP_SNARE_DOG && traps[t].r==dogX && traps[t].c==dogY){
      traps[t].active=false;
      dog_skip_turns += 1;
      drawHudDog(false, -1, false);
      tcaSelect(DOG_CH); dspDog.setCursor(80,60); dspDog.print("SNARED!"); dspDog.display();
      return true; // หยุดเดินเทิร์นนี้
    }
  }
  return false;
}

// =====================================================
// per-turn (แสดง STEP 1.5 วิ ก่อนเดินจริง)
// =====================================================
void showTouchHintOnHUDs(){
  drawHudCat(turnNow==CAT_TURN, -1, false);
  drawHudDog(turnNow==DOG_TURN, -1, false);
}

void run_cat_turn(){
  showTouchHintOnHUDs();             // “TOUCH to roll…”
  int steps = rollStepsByTouch();

  drawHudCat(false, steps, false);
  drawHudDog(false, steps, false);
  delay(1500);

  bool moved=false, blocked=false;
  for(int s=0; s<steps; s++){
    int nx = catX + dx[dirCat];
    int ny = catY + dy[dirCat];
    if (!is_valid_move_cat_next(nx,ny)) { blocked=true; break; }
    catX = nx; catY = ny; moved=true;

    check_cat_trap_here();                // กับดักของแมว
    if (dog_attacks_cat_immediate()) return; // ทับระหว่างทาง ⇒ -1
  }
  if (blocked) { drawHudCat(false, steps, true); delay(1500); }
  if (moved) { drawMap(); }
  drawHudCat(); drawHudDog();
  check_cat_win();
}

void run_dog_turn(){
  showTouchHintOnHUDs();
  int steps = rollStepsByTouch();

  drawHudCat(false, steps, false);
  drawHudDog(false, steps, false);
  delay(1500);

  bool touched_cat_any=false, blocked=false;
  for(int s=0; s<steps; s++){
    int nx = dogX + dx[dirDog];
    int ny = dogY + dy[dirDog];
    if (!is_valid_move_dog_next(nx,ny)) { blocked=true; break; }
    dogX = nx; dogY = ny;

    if (check_dog_trap_here_and_snare()){ break; } // กับดักหมา → หยุดทันที
    if (dogX==catX && dogY==catY) touched_cat_any=true;
  }
  if (blocked) { drawHudDog(false, steps, true); delay(1500); }
  drawMap();
  drawHudCat(); drawHudDog();

  bool ended_on_cat = (dogX==catX && dogY==catY);
  if (ended_on_cat && !gameOver)       apply_cat_damage_half(2); // -1.0
  else if (touched_cat_any && !gameOver) apply_cat_damage_half(1); // -0.5
}

// =====================================================
// setup / loop
// =====================================================
void setup(){
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);
  randomSeed(esp_random());

  pinMode(BTN1, INPUT_PULLUP);
  pinMode(BTN2, INPUT_PULLUP);
  pinMode(BTN3, INPUT_PULLUP);

  // init displays
  tcaSelect(MAP_CH);
  if (!dspMap.begin(0x3C, true)) { Serial.println("map (ch1) init fail"); }
  tcaSelect(CAT_CH);
  if (!dspCat.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { Serial.println("cat HUD (ch0) fail"); }
  tcaSelect(DOG_CH);
  if (!dspDog.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { Serial.println("dog HUD (ch2) fail"); }

  build_simple_randomish_map();
  spawn_traps();  // วางกับดัก
  drawMap(); drawHudCat(); drawHudDog();
}

void loop(){
  if (gameOver) return;

  if (turnNow==CAT_TURN){
    if (pressedOnce(BTN3, latchBtn3, lastEdge3)){ dirCat=(dirCat+1)%4; drawHudCat(); }
    if (pressedOnce(BTN2, latchBtn2, lastEdge2)){
      run_cat_turn();
      if (!gameOver){ turnNow=DOG_TURN; drawMap(); drawHudCat(); drawHudDog(); }
    }
  } else { // DOG_TURN
    if (dog_skip_turns > 0){
      dog_skip_turns--;
      drawHudDog(); tcaSelect(DOG_CH); dspDog.setCursor(64,60); dspDog.print("SKIP"); dspDog.display();
      delay(800);
      turnNow = CAT_TURN;
      drawMap(); drawHudCat(); drawHudDog();
      return;
    }
    if (pressedOnce(BTN1, latchBtn1, lastEdge1)){ dirDog=(dirDog+1)%4; drawHudDog(); }
    if (pressedOnce(BTN2, latchBtn2, lastEdge2)){
      run_dog_turn();
      if (!gameOver){ turnNow=CAT_TURN; drawMap(); drawHudCat(); drawHudDog(); }
    }
  }

  delay(5);
}
