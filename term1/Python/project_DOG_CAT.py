# # === smart_map_game.py ===
# import random
# import time
# from collections import deque

# random.seed(100)

# ROWS = 7
# COLS = 20

# EMPTY = '.'
# WALL = '#'
# CAT = 'C'
# DOG = 'D'
# GOAL = 'G'

# dx = [0, -1, 1, 0, 0]
# dy = [0, 0, 0, -1, 1]

# catX, catY = 0, 0
# dogX, dogY = 6, 0
# goalX, goalY = 6, 19
# catHP = 1.0
# gameOver = False

# # แผนที่ที่กำหนดเอง
# predefined_maps = {
#     '1': [
#         "......#......#....#.",
#         "..#.................",
#         ".....#.#.#..........",
#         "...#......# #.......",
#         "......#..#......#...",
#         "#...#.........#.....",
#         ".......#....#......."
#     ],
#     '2': [
#         "#####...............",
#         "#...................",
#         "#..#######..........",
#         "#...........#####...",
#         "#######............#",
#         "...............#####",
#         "...................."
#     ],
#     '3': [
#         "....................",
#         "######..######......",
#         "......##......####..",
#         "..####..........##..",
#         "..##......######....",
#         "......######........",
#         "...................."
#     ]
# }

# def print_board():
#     print("\n---- Game Board ----")
#     for i in range(ROWS):
#         row = ''
#         for j in range(COLS):
#             if i == catX and j == catY:
#                 row += CAT
#             elif i == dogX and j == dogY:
#                 row += DOG
#             elif i == goalX and j == goalY:
#                 row += GOAL
#             else:
#                 row += baseMap[i][j]
#             row += ' '
#         print(row)
#     print(f"\nCat HP: {catHP:.1f}")

# def bfs_path_exists(sx, sy, tx, ty, grid):
#     visited = [[False] * COLS for _ in range(ROWS)]
#     queue = deque([(sx, sy)])
#     visited[sx][sy] = True

#     while queue:
#         x, y = queue.popleft()
#         if (x, y) == (tx, ty):
#             return True
#         for d in range(1, 5):
#             nx, ny = x + dx[d], y + dy[d]
#             if 0 <= nx < ROWS and 0 <= ny < COLS:
#                 if not visited[nx][ny] and grid[nx][ny] != WALL:
#                     visited[nx][ny] = True
#                     queue.append((nx, ny))
#     return False

# def load_predefined_map(map_id):
#     global baseMap
#     raw_map = predefined_maps.get(map_id)
#     if not raw_map:
#         print("Invalid map ID. Using default map 1.")
#         raw_map = predefined_maps['1']
#     baseMap = [list(row) for row in raw_map]

#     if not bfs_path_exists(catX, catY, goalX, goalY, baseMap):
#         print("[ERROR] Cat cannot reach the goal in this map.")
#         exit()
#     if not bfs_path_exists(dogX, dogY, goalX, goalY, baseMap):
#         print("[ERROR] Dog cannot reach the goal in this map.")
#         exit()

# def move_entity(ex, ey, dir, steps, is_dog):
#     global catHP, gameOver
#     for s in range(1, steps + 1):
#         nx = max(0, min(ex + dx[dir], ROWS - 1))
#         ny = max(0, min(ey + dy[dir], COLS - 1))
#         if baseMap[nx][ny] == WALL:
#             print("  ► Hit a wall; stopping.")
#             break
#         ex, ey = nx, ny
#         if is_dog and ex == catX and ey == catY:
#             if s < steps:
#                 catHP -= 0.5
#                 print("  ► Dog passed through Cat! Cat loses 0.5 HP.")
#                 if catHP <= 0:
#                     catHP = 0
#                     print("  ► Cat died! Dog wins!")
#                     gameOver = True
#             else:
#                 catHP = 0
#                 print("  ► Dog landed on Cat! Cat is killed instantly! Dog wins!")
#                 gameOver = True
#             if gameOver:
#                 return ex, ey
#     return ex, ey

# # เริ่มเกม
# print("=== Cat vs Dog ===")
# map_choice = input("Choose map (1 / 2 / 3): ").strip()
# load_predefined_map(map_choice)
# print_board()

# while not gameOver:
#     print("\n-- Cat's turn --")
#     try:
#         cdir = int(input("  Direction (1=↑, 2=↓, 3=←, 4=→): "))
#         csteps = int(input("  Steps (1-4): "))
#         catX, catY = move_entity(catX, catY, cdir, csteps, False)
#     except ValueError:
#         print("  Invalid input. Skipping turn.")

#     if catX == goalX and catY == goalY:
#         print("Cat reached the goal! Cat wins!")
#         break

#     print_board()

#     print("\n-- Dog's turn --")
#     ddir = int(input("  Direction (1=↑, 2=↓, 3=←, 4=→): "))
#     dsteps = random.randint(1, 4)
#     print(f"  Dog moves dir={ddir} steps={dsteps}")
#     dogX, dogY = move_entity(dogX, dogY, ddir, dsteps, True)

#     print_board()
#     time.sleep(1)

#     if catHP <= 0:
#         break

import random
import time

# เริ่มต้นการสุ่ม
random.seed(100)
level = random.randint(1, 3)

# ขนาดของบอร์ดเกม
ROWS = 7
COLS = 20

# สัญลักษณ์ที่ใช้ในเกม
EMPTY = '.'
WALL = '#'
CAT = 'C'
DOG = 'D'
GOAL = 'G'
ITEMCAT = 'IC'
ITEMDOG = 'ID'

# ทิศทางการเคลื่อนที่: ขึ้น, ซ้าย, ขวา, ลง
dx = [0, 0, -1, 1]  # การเคลื่อนที่ในแนวนอน (บน, ล่าง, ซ้าย, ขวา)
dy = [-1, 1, 0, 0]  # การเคลื่อนที่ในแนวตั้ง (ขึ้น, ลง, ซ้าย, ขวา) แต่ใช้จริง จะใช้้คู่ ซ้าย ขวา บน ล่าง

# ตำแหน่งเริ่มต้นของแมว, หมา และจุดหมาย
catX, catY = 0, 0
dogX, dogY = 6, 0
goalX, goalY = 6, 19
catHP = 1.0
gameOver = False

# แผนที่ที่กำหนดไว้ล่วงหน้าสำหรับแต่ละระดับ
predefined_maps = {
    '1': [
        "......#......#....#.",
        "..#.................",
        ".....#.#...........#",
        "...#......# #.......",
        "......#..#......#...",
        "#...#.........#.....",
        ".......#....#......."
    ],
    '2': [
        "...##.......#.......",
        "#................#..",
        "#..#.....#..........",
        "#...........##....#.",
        "#.#...#............#",
        "...............#...#",
        ".......##..........."
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

# ฟังก์ชันเพื่อแสดงผลบอร์ดเกม
def print_board(base_map):
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
                row += base_map[i][j]
            row += ' '
        print(row)

# ฟังก์ชันเพื่อเลือกแผนที่ตามระดับ
def get_map(level):
    level = str(level)
    return predefined_maps.get(level, predefined_maps[level])

# ฟังก์ชันเช็คว่าตำแหน่งที่ต้องการเดินไปมีกำแพงหรือไม่
def is_valid_move_cat(x, y, base_map):
    if 0 <= x < ROWS and 0 <= y < COLS and base_map[x][y] != WALL:
        return True
    return False
def is_valid_move_dog(x, y, base_map):
    if 0 <= x < ROWS and 0 <= y < COLS and base_map[x][y] != WALL:
        if x == goalX and y == goalY:
            return False  # หมาไม่สามารถเดินทับเส้นชัยได้
        return True
    return False

# ฟังก์ชันที่หมาจะโจมตีแมว
def dog_attacks_cat():
    global catHP, gameOver
    
    # ตรวจสอบว่าเดินทับแมว
    if catX == dogX and catY == dogY:
        catHP -= 1  # ลดเลือดแมว 1 หน่วยหากหมาทับแมว
        print("หมาทับแมว! เลือดแมวลดลง -1")
        print("แมวตายแล้ว!")
        print("หมาชนะ!")
        gameOver = True
        return True
    return False

# ฟังก์ชันให้ผู้เล่นเลือกทิศทางการเดิน
def choose_direction():
    print("เลือกทิศทางการเดิน:")
    print("1. ซ้าย (←)")
    print("2. ขวา (→)")
    print("3. ขึ้น (↑)")
    print("4. ลง (↓)")
    
    while True:
    # รับการเลือกจากผู้เล่น
        try:
            choice = int(input("เลือกทิศทาง (1-4): "))
            if choice < 1 or choice > 4:
                raise ValueError
            break
        except ValueError:
            print("กรุณากรอกตัวเลข 1-4 เท่านั้น!")
    return choice - 1  # คืนค่าตัวเลขที่ตรงกับ index ของการเคลื่อนที่
# ฟังก์ชันเช็คว่าแมวชนะไหม
def check_cat_win():
        if catX == goalX and catY == goalY:
            print("แมวถึงจุดหมายแล้ว!")
            print("แมวชนะ!")
            return True
# ฟังก์ชันเกมลูปหลัก
def game_loop():
    global catX, catY, dogX, dogY, gameOver
    # level = '1'  # เลือกระดับแผนที่เริ่มต้น
    base_map = get_map(level)
    # ลูปหลักของเกม
    while not gameOver:
        print_board(base_map)
        # ให้แมวเลือกทิศทางการเดิน
        print("\nแมวกำลังเลือกทิศทาง...")
        cat_direction = choose_direction()
        cat_distance = random.randint(1, 4)  # สุ่มระยะเดินของแมว (1-4 ช่อง)
        print(f"แมวเดิน {cat_distance} ช่อง")
        cat_distance = int(input("แมวเดินกี่ช่อง? (test)"))
        # เดินแมว
        for _ in range(cat_distance):
            new_catX = catX + dx[cat_direction]
            new_catY = catY + dy[cat_direction]
            if is_valid_move_cat(new_catX, new_catY, base_map):
                catX, catY = new_catX, new_catY
            else:
                print("แมวติดกับกำแพง!")
                break
        print_board(base_map)

        gameOver = dog_attacks_cat()
        # ตรวจสอบว่าแมวถึงจุดหมายหรือไม่
        gameOver = check_cat_win()
        if gameOver:
            break
        # ให้หมาเลือกทิศทางการเดิน
        print("\nหมากำลังเลือกทิศทาง...")
        dog_direction = choose_direction()
        dog_distance = random.randint(1, 4)  # สุ่มระยะเดินของหมา (1-4 ช่อง)
        dog_distance = int(input("หมาเดินกี่ช่อง? (test)"))
        print(f"หมาเดิน {dog_distance} ช่อง")
        
        # เดินหมา
        for _ in range(dog_distance):
            new_dogX = dogX + dx[dog_direction]
            new_dogY = dogY + dy[dog_direction]
            if is_valid_move_dog(new_dogX, new_dogY, base_map):
                dogX, dogY = new_dogX, new_dogY
            else:
                print("หมาติดกับกำแพง!")
                break
        gameOver = dog_attacks_cat()

# เรียกใช้ฟังก์ชันเกมลูปเพื่อเริ่มเกม
game_loop()
print("จบเกม!")