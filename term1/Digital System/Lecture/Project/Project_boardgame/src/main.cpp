// #include <Arduino.h>

// #define ROWS 7
// #define COLS 30

// char map[ROWS][COLS];
// float catHP = 1.0;

// int catX = 0, catY = 0;
// int dogX = ROWS - 1, dogY = COLS - 1;

// int goalX = ROWS - 1, goalY = COLS - 1;

// // ตัวแทนบนแผนที่
// #define EMPTY '.'
// #define WALL '#'
// #define CAT 'C'
// #define DOG 'D'
// #define GOAL 'G'

// // สุ่มกำแพงแบบง่าย
// void generateWalls(int count) {
//   int placed = 0;
//   while (placed < count) {
//     int x = random(ROWS);
//     int y = random(COLS);
//     if (map[x][y] == EMPTY && !(x == catX && y == catY) && !(x == dogX && y == dogY) && !(x == goalX && y == goalY)) {
//       map[x][y] = WALL;
//       placed++;
//     }
//   }
// }

// // แสดงแผนที่
// void printMap() {
//   for (int i = 0; i < ROWS; i++) {
//     for (int j = 0; j < COLS; j++) {
//       if (i == catX && j == catY) Serial.print(CAT);
//       else if (i == dogX && j == dogY) Serial.print(DOG);
//       else Serial.print(map[i][j]);
//       Serial.print(' ');
//     }
//     Serial.println();
//   }
//   Serial.println();
// }

// // เช็กจบเกม
// bool checkGameOver() {
//   if (catX == dogX && catY == dogY) {
//     Serial.println("😈 Dog caught the cat! Dog wins!");
//     return true;
//   }
//   if (catX == goalX && catY == goalY) {
//     Serial.println("😸 Cat reached the goal! Cat wins!");
//     return true;
//   }
//   if (catHP <= 0) {
//     Serial.println("💀 Cat died from damage. Dog wins!");
//     return true;
//   }
//   return false;
// }

// // สุ่มทิศทาง 1=บน 2=ล่าง 3=ซ้าย 4=ขว
// void moveDog() {
//   int dir = random(1, 5); // 1 to 4
//   int step = random(1, 5); // 1 to 4
//   int newX = dogX, newY = dogY;

//   for (int i = 0; i < step; i++) {
//     int tempX = newX, tempY = newY;

//     if (dir == 1 && newX > 0) tempX--;
//     else if (dir == 2 && newX < ROWS - 1) tempX++;
//     else if (dir == 3 && newY > 0) tempY--;
//     else if (dir == 4 && newY < COLS - 1) tempY++;

//     if (map[tempX][tempY] == WALL) break;

//     newX = tempX;
//     newY = tempY;

//     // ถ้าเดินผ่านแมว
//     if (newX == catX && newY == catY) {
//       if (i == step - 1) {
//         catHP = 0;
//         return;
//       } else {
//         catHP -= 0.5;
//         Serial.println("🐾 Dog passed over the cat. HP -0.5");
//       }
//     }
//   }

//   dogX = newX;
//   dogY = newY;
// }

// void setup() {
//   Serial.begin(115200);
//   delay(1000);
//   randomSeed(analogRead(0));

//   // เตรียมแผนที่ว่าง
//   for (int i = 0; i < ROWS; i++) {
//     for (int j = 0; j < COLS; j++) {
//       map[i][j] = EMPTY;
//     }
//   }

//   map[goalX][goalY] = GOAL;
//   generateWalls(40);

//   printMap();
// }

// void loop() {
//   delay(1500);

//   moveDog();
//   printMap();

//   Serial.print("🐱 Cat HP: ");
//   Serial.println(catHP);

//   if (checkGameOver()) {
//     while (true); // จบเกม หยุด loop
//   }
// }



// src/main.cpp

#include <Arduino.h>

#define ROWS 7
#define COLS 30

// Entities on the board
enum Tile { EMPTY='.', WALL='#', CAT='C', DOG='D', GOAL='G' };

// Game state
char baseMap[ROWS][COLS];
int catX, catY;
int dogX, dogY;
int goalX, goalY;
float catHP = 1.0;
bool gameOver = false;

// Simple 4‐way offsets: 1=up,2=down,3=left,4=right
const int dx[5] = {0, -1, +1,  0,  0};
const int dy[5] = {0,  0,  0, -1, +1};

// Utility: print the current board + HP
void printBoard() {
  Serial.println(F("\n──── Game Board ────"));
  for (int i = 0; i < ROWS; i++) {
    for (int j = 0; j < COLS; j++) {
      char c = baseMap[i][j];
      if (i==catX && j==catY)      c = CAT;
      else if (i==dogX && j==dogY) c = DOG;
      else if (i==goalX && j==goalY) c = GOAL;
      Serial.print(c);
      Serial.print(' ');
    }
    Serial.println();
  }
  Serial.print(F("\nCat HP: "));
  Serial.println(catHP, 1);
}

// Carve a random simple path from (sx,sy) to (gx,gy),
// then sprinkle other walls at density p (0.0–1.0)
void generateMap(float wallDensity=0.25) {
  // start with all walls
  for (int i=0;i<ROWS;i++)
    for(int j=0;j<COLS;j++)
      baseMap[i][j] = WALL;

  // random walk path
  int x = catX, y = catY;
  baseMap[x][y] = EMPTY;
  while (x!=goalX || y!=goalY) {
    int dir = random(1,5);
    int nx = constrain(x + dx[dir], 0, ROWS-1);
    int ny = constrain(y + dy[dir], 0, COLS-1);
    // move only if toward goal with some randomness
    if (random(0,2)==0 ||
       (abs(goalX-x) > abs(goalY-y) && nx!=x) ||
       (abs(goalY-y) >= abs(goalX-x) && ny!=y)) {
      x = nx; y = ny;
      baseMap[x][y] = EMPTY;
    }
  }

  // sprinkle extra empty vs walls
  for (int i=0;i<ROWS;i++) for (int j=0;j<COLS;j++) {
    if ((i==catX&&j==catY)||(i==goalX&&j==goalY)) continue;
    if (baseMap[i][j]==EMPTY) continue;
    if (random(1000)/1000.0 > wallDensity) baseMap[i][j] = EMPTY;
  }
}

// Attempt to move an entity; returns final (x,y).  
// For dog, applies collision rules to catHP.
void moveEntity(int &ex, int &ey, int dir, int steps, bool isDog) {
  for (int s=1; s<=steps; s++) {
    int nx = constrain(ex + dx[dir], 0, ROWS-1);
    int ny = constrain(ey + dy[dir], 0, COLS-1);
    if (baseMap[nx][ny]==WALL) {
      Serial.println(F("  ► Hit a wall; stopping."));
      break;
    }
    ex = nx; ey = ny;
    if (isDog && ex==catX && ey==catY) {
      if (s < steps) {
        catHP -= 0.5;
        Serial.println(F("  ► Dog passed through Cat! Cat loses 0.5 HP."));
        if (catHP <= 0) {
          catHP = 0; 
          Serial.println(F("  ► Cat died! Dog wins!"));
          gameOver = true;
        }
      } else {
        catHP = 0;
        Serial.println(F("  ► Dog landed on Cat! Cat is killed instantly! Dog wins!"));
        gameOver = true;
      }
      if (gameOver) return;
    }
  }
}

void setup() {
  Serial.begin(115200);
  while(!Serial){}  // wait for Serial
  randomSeed(analogRead(0));

  // Initial positions
  catX = 0;      catY = 0;
  dogX = ROWS-1; dogY = 0;
  goalX = ROWS-1; goalY = COLS-1;

  generateMap(0.25);
  Serial.println(F("=== Cat vs Dog on ESP32 ==="));
  printBoard();
}

void loop() {
  if (gameOver) {
    // do nothing more
    delay(1000);
    return;
  }

  // 1) Cat's move
  Serial.println(F("\n-- Cat's turn --"));
  Serial.println(F("  Enter: <dir(1-4)> <steps(1-4)>"));
  while (!Serial.available()) { delay(10); }
  int cdir = Serial.parseInt();
  int csteps = Serial.parseInt();
  moveEntity(catX, catY, cdir, csteps, false);
  if (catX==goalX && catY==goalY) {
    Serial.println(F("🏁 Cat reached the goal! Cat wins!"));
    gameOver = true;
    printBoard();
    return;
  }
  printBoard();

  // 2) Dog's move
  Serial.println(F("\n-- Dog's turn --"));
  Serial.println(F("  Enter: <dir(1-4)> <steps(1-4)>"));
  while (!Serial.available()) { delay(10); }
  int ddir = Serial.parseInt();
  int dsteps = Serial.parseInt();
  moveEntity(dogX, dogY, ddir, dsteps, true);
  printBoard();
}

  