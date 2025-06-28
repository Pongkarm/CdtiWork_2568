# === smart_map_game.py ===
import random
import time
from collections import deque

random.seed(100)

ROWS = 7
COLS = 20

EMPTY = '.'
WALL = '#'
CAT = 'C'
DOG = 'D'
GOAL = 'G'

dx = [0, -1, 1, 0, 0]
dy = [0, 0, 0, -1, 1]

catX, catY = 0, 0
dogX, dogY = 6, 0
goalX, goalY = 6, 19
catHP = 1.0
gameOver = False

# แผนที่ที่กำหนดเอง
predefined_maps = {
    '1': [
        "......#......#....#.",
        "..#.................",
        ".....#.#.#..........",
        "...#......# #.......",
        "......#..#......#...",
        "#...#.........#.....",
        ".......#....#......."
    ],
    '2': [
        "#####...............",
        "#...................",
        "#..#######..........",
        "#...........#####...",
        "#######............#",
        "...............#####",
        "...................."
    ],
    '3': [
        "....................",
        "######..######......",
        "......##......####..",
        "..####..........##..",
        "..##......######....",
        "......######........",
        "...................."
    ]
}

def print_board():
    print("\n---- Game Board ----")
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
    print(f"\nCat HP: {catHP:.1f}")

def bfs_path_exists(sx, sy, tx, ty, grid):
    visited = [[False] * COLS for _ in range(ROWS)]
    queue = deque([(sx, sy)])
    visited[sx][sy] = True

    while queue:
        x, y = queue.popleft()
        if (x, y) == (tx, ty):
            return True
        for d in range(1, 5):
            nx, ny = x + dx[d], y + dy[d]
            if 0 <= nx < ROWS and 0 <= ny < COLS:
                if not visited[nx][ny] and grid[nx][ny] != WALL:
                    visited[nx][ny] = True
                    queue.append((nx, ny))
    return False

def load_predefined_map(map_id):
    global baseMap
    raw_map = predefined_maps.get(map_id)
    if not raw_map:
        print("Invalid map ID. Using default map 1.")
        raw_map = predefined_maps['1']
    baseMap = [list(row) for row in raw_map]

    if not bfs_path_exists(catX, catY, goalX, goalY, baseMap):
        print("[ERROR] Cat cannot reach the goal in this map.")
        exit()
    if not bfs_path_exists(dogX, dogY, goalX, goalY, baseMap):
        print("[ERROR] Dog cannot reach the goal in this map.")
        exit()

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
map_choice = input("Choose map (1 / 2 / 3): ").strip()
load_predefined_map(map_choice)
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
        print("Cat reached the goal! Cat wins!")
        break

    print_board()

    print("\n-- Dog's turn --")
    ddir = int(input("  Direction (1=↑, 2=↓, 3=←, 4=→): "))
    dsteps = random.randint(1, 4)
    print(f"  Dog moves dir={ddir} steps={dsteps}")
    dogX, dogY = move_entity(dogX, dogY, ddir, dsteps, True)

    print_board()
    time.sleep(1)

    if catHP <= 0:
        break
