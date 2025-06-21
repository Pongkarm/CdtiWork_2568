import random
import time

ROWS = 7
COLS = 30

# ตัวแทนสัญลักษณ์
EMPTY = '.'
WALL = '#'
CAT = 'C'
DOG = 'D'
GOAL = 'G'

# ทิศทาง: 1=บน, 2=ล่าง, 3=ซ้าย, 4=ขว
dx = [0, -1, 1, 0, 0]
dy = [0, 0, 0, -1, 1]

# ตำแหน่งเริ่มต้น
catX, catY = 0, 0
dogX, dogY = ROWS - 1, 0
goalX, goalY = ROWS - 1, COLS - 1
catHP = 1.0
gameOver = False

# สร้างแผนที่เริ่มต้น
baseMap = [[WALL for _ in range(COLS)] for _ in range(ROWS)]


def print_board():
    print("\n──── Game Board ────")
    for i in range(ROWS):
        row = ''
        for j in range(COLS):
            if i == catX and j == catY:
                row += CAT
            elif i == dogX and j == dogY:
                row += DOG
            elif i == goalX and j == goalY:
                row += GOAL
            else:
                row += baseMap[i][j]
            row += ' '
        print(row)
    print(f"\n🐱 Cat HP: {catHP:.1f}")


def generate_map(wall_density=0.25):
    global baseMap
    baseMap = [[WALL for _ in range(COLS)] for _ in range(ROWS)]

    x, y = catX, catY
    baseMap[x][y] = EMPTY

    while x != goalX or y != goalY:
        dir = random.randint(1, 4)
        nx = max(0, min(x + dx[dir], ROWS - 1))
        ny = max(0, min(y + dy[dir], COLS - 1))

        if random.choice([True, False]) or \
           (abs(goalX - x) > abs(goalY - y) and nx != x) or \
           (abs(goalY - y) >= abs(goalX - x) and ny != y):
            x, y = nx, ny
            baseMap[x][y] = EMPTY

    for i in range(ROWS):
        for j in range(COLS):
            if (i == catX and j == catY) or (i == goalX and j == goalY):
                continue
            if baseMap[i][j] == EMPTY:
                continue
            if random.random() > wall_density:
                baseMap[i][j] = EMPTY


def move_entity(ex, ey, dir, steps, is_dog):
    global catHP, gameOver
    for s in range(1, steps + 1):
        nx = max(0, min(ex + dx[dir], ROWS - 1))
        ny = max(0, min(ey + dy[dir], COLS - 1))
        if baseMap[nx][ny] == WALL:
            print("  ► Hit a wall; stopping.")
            break
        ex, ey = nx, ny
        if is_dog and ex == catX and ey == catY:
            if s < steps:
                catHP -= 0.5
                print("  ► Dog passed through Cat! Cat loses 0.5 HP.")
                if catHP <= 0:
                    catHP = 0
                    print("  ► Cat died! Dog wins!")
                    gameOver = True
            else:
                catHP = 0
                print("  ► Dog landed on Cat! Cat is killed instantly! Dog wins!")
                gameOver = True
            if gameOver:
                return ex, ey
    return ex, ey


# เริ่มเกม
print("=== Cat vs Dog ===")
generate_map()
print_board()

while not gameOver:
    print("\n-- Cat's turn --")
    try:
        cdir = int(input("  Direction (1=↑, 2=↓, 3=←, 4=→): "))
        csteps = int(input("  Steps (1-4): "))
        catX, catY = move_entity(catX, catY, cdir, csteps, False)
    except ValueError:
        print("  Invalid input. Skipping turn.")

    if catX == goalX and catY == goalY:
        print("🏁 Cat reached the goal! Cat wins!")
        break

    print_board()

    print("\n-- Dog's turn --")
    ddir = random.randint(1, 4)
    dsteps = random.randint(1, 4)
    print(f"  Dog moves dir={ddir} steps={dsteps}")
    dogX, dogY = move_entity(dogX, dogY, ddir, dsteps, True)

    print_board()
    time.sleep(1)

    if catHP <= 0:
        break

