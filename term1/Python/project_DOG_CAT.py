import random
import time

# -------------------- CONFIG --------------------
USE_RANDOM_MAP = True   # ตั้ง True เพื่อใช้แผนที่สุ่ม
DENSITY_BY_LEVEL = {1: 0.16, 2: 0.20, 3: 0.24}  # สัดส่วนกำแพงต่อพื้นที่
MIN_WALL_SPACING = 1    # ระยะกระจายกำแพง (Chebyshev) 1 = ไม่ให้ติดกันแม้ทแยง
MAX_ITEMS = 10           # จำนวนไอเทมรวมสูงสุดต่อแมพ
# ------------------------------------------------

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
# ไอเทม (ใช้ตัวอักษรเดี่ยวเพื่อพิมพ์พอดีช่อง)
CAT_ITEM_DISPLAY = 'F'  # Fish
DOG_ITEM_DISPLAY = 'L'  # Lock/Chain

# ทิศทางการเคลื่อนที่: ซ้าย, ขวา, ขึ้น, ลง (ตามเมนู)
dx = [0, 0, -1, 1]
dy = [-1, 1, 0, 0]

# ตำแหน่งเริ่มต้นของแมว, หมา และจุดหมาย
catX, catY = 0, 0
dogX, dogY = 6, 0
goalX, goalY = 6, 19
catHP = 1.0
gameOver = False

# สถานะไอเทม/เอฟเฟกต์
cat_items = set()   # {(r,c)} ปลา
dog_items = set()   # {(r,c)} โซ่ล็อก
cat_can_phase_next = False   # เก็บปลาแล้ว: เปิดใช้ทะลุกำแพง "ตาถัดไป"
cat_phasing_active = False   # สถานะกำลังทะลุกำแพงใน "ตานี้"
cat_skip_turns = 0           # โดนล็อกจากโซ่ ข้ามกี่ตา

# แผนที่ที่กำหนดไว้ล่วงหน้า
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

# -------------------- RANDOM MAP GEN --------------------
def _in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS

def _carve_random_corridor(rng, start, goal):
    """ สร้างคอร์ริดอร์แบบสุ่มคดเคี้ยวจาก start -> goal """
    path = [start]
    r, c = start
    gr, gc = goal
    while (r, c) != (gr, gc):
        steps = []
        if gr > r: steps.append((1, 0))
        elif gr < r: steps.append((-1, 0))
        if gc > c: steps.append((0, 1))
        elif gc < c: steps.append((0, -1))
        rng.shuffle(steps)
        if rng.random() < 0.25:
            steps += [(-1,0),(1,0),(0,-1),(0,1)]
            rng.shuffle(steps)
        moved = False
        for dr, dc in steps:
            nr, nc = r+dr, c+dc
            if _in_bounds(nr, nc):
                r, c = nr, nc
                path.append((r, c))
                moved = True
                break
        if not moved:  # กันหลุดลูปในกรณีแปลก ๆ
            break
    return path

def generate_random_map(level_num):
    rng = random.Random(time.time_ns())
    density = DENSITY_BY_LEVEL.get(level_num, 0.20)
    target_walls = int(round(density * ROWS * COLS))

    start_cat = (catX, catY)
    start_dog = (dogX, dogY)
    goal = (goalX, goalY)

    corridor1 = _carve_random_corridor(rng, start_cat, start_dog)
    corridor2 = _carve_random_corridor(rng, start_dog, goal)
    corridor = set(corridor1 + corridor2)

    reserved = corridor | {start_cat, start_dog, goal}
    cells = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) not in reserved]
    rng.shuffle(cells)

    walls = set()
    def spacing_ok(cell):
        r, c = cell
        for rr in range(r - MIN_WALL_SPACING, r + MIN_WALL_SPACING + 1):
            for cc in range(c - MIN_WALL_SPACING, c + MIN_WALL_SPACING + 1):
                if (rr, cc) in walls:
                    return False
        return True

    for rc in cells:
        if len(walls) >= target_walls:
            break
        if spacing_ok(rc):
            walls.add(rc)

    grid = [[EMPTY for _ in range(COLS)] for __ in range(ROWS)]
    for r, c in walls: grid[r][c] = WALL
    for r, c in corridor: grid[r][c] = EMPTY
    sr, sc = start_cat; grid[sr][sc] = EMPTY
    sr, sc = start_dog; grid[sr][sc] = EMPTY
    sr, sc = goal;     grid[sr][sc] = EMPTY

    return ["".join(row) for row in grid]
# --------------------------------------------------------

# -------------------- ITEMS: SPAWN & DISPLAY --------------------
def spawn_items(base_map):
    """ สุ่มไอเทมรวมไม่เกิน MAX_ITEMS, ไม่ทับกัน/กำแพง/ตำแหน่งสำคัญ """
    global cat_items, dog_items
    rng = random.Random(time.time_ns())

    # สุ่มจำนวนรวม (อย่างน้อย 2 เพื่อมีโอกาสของทั้งสองฝ่าย)
    total = rng.randint(2, MAX_ITEMS) if MAX_ITEMS >= 2 else MAX_ITEMS
    # สุ่มแบ่งให้แต่ละฝ่าย (มีอย่างน้อย 1 ชิ้นถ้า total >= 2)
    if total >= 2:
        n_cat = rng.randint(1, total - 1)
        n_dog = total - n_cat
    else:
        n_cat = total
        n_dog = 0

    reserved = {(catX, catY), (dogX, dogY), (goalX, goalY)}
    # ห้ามเกิดบนกำแพง
    empties = [(r, c) for r in range(ROWS) for c in range(COLS)
               if base_map[r][c] != WALL and (r, c) not in reserved]
    rng.shuffle(empties)

    cat_items = set()
    dog_items = set()

    def take_cells(n, taken):
        out = []
        for rc in empties:
            if rc in taken or rc in out:
                continue
            out.append(rc)
            if len(out) == n:
                break
        return out

    cat_cells = take_cells(n_cat, cat_items | dog_items)
    for rc in cat_cells: cat_items.add(rc)
    dog_cells = take_cells(n_dog, cat_items | dog_items)
    for rc in dog_cells: dog_items.add(rc)

def print_board(base_map):
    print("\n---- Game Board ----")
    for i in range(ROWS):
        row = ''
        for j in range(COLS):
            ch = base_map[i][j]
            # overlay ลำดับความสำคัญ: ตัวละคร > เส้นชัย > ไอเทม > พื้น/กำแพง
            if i == catX and j == catY:
                ch = CAT
            elif i == dogX and j == dogY:
                ch = DOG
            elif i == goalX and j == goalY:
                ch = GOAL
            elif (i, j) in cat_items:
                ch = CAT_ITEM_DISPLAY
            elif (i, j) in dog_items:
                ch = DOG_ITEM_DISPLAY
            row += ch + ' '
        print(row)
    status = []
    if cat_phasing_active:
        status.append("PHASE:ON")
    elif cat_can_phase_next:
        status.append("PHASE:NEXT")
    if cat_skip_turns > 0:
        status.append(f"LOCK:{cat_skip_turns}")
    print(f"HP แมว: {catHP:.2f}  |  " + "  ".join(status))

# -------------------- VALIDATION --------------------
def get_map(level):
    if USE_RANDOM_MAP:
        print(f"\n[แผนที่สุ่ม] Level {level} | density≈{DENSITY_BY_LEVEL.get(level, 0.20):.0%} | spacing={MIN_WALL_SPACING}")
        return generate_random_map(level)
    level = str(level)
    return predefined_maps.get(level, predefined_maps[level])

def is_valid_move_cat(x, y, base_map):
    # ถ้ากำลังทะลุกำแพงอยู่: อนุญาตทุกช่องที่อยู่ในขอบเขต
    if cat_phasing_active:
        return 0 <= x < ROWS and 0 <= y < COLS
    # ปกติ: ห้ามชนกำแพง
    if 0 <= x < ROWS and 0 <= y < COLS and base_map[x][y] != WALL:
        return True
    return False

def is_valid_move_dog(x, y, base_map):
    if 0 <= x < ROWS and 0 <= y < COLS and base_map[x][y] != WALL:
        if x == goalX and y == goalY:
            return False  # หมาไม่สามารถเดินทับเส้นชัยได้
        return True
    return False

# -------------------- DAMAGE / WIN-CHECK --------------------
def apply_cat_damage(amount, cause_text):
    global catHP, gameOver
    if amount <= 0 or gameOver:
        return
    catHP = round(catHP - amount, 2)
    print(cause_text)
    print(f"เลือดแมวลดลง -{amount:.1f}  | เหลือ {catHP:.2f}")
    if catHP <= 0:
        print("แมวตายแล้ว!")
        print("หมาชนะ!")
        gameOver = True

def dog_attacks_cat():
    if catX == dogX and catY == dogY:
        apply_cat_damage(1.0, "หมาทับแมว!")
        return True if gameOver else False
    return False

def choose_direction():
    print("เลือกทิศทางการเดิน:")
    print("1. ซ้าย (←)")
    print("2. ขวา (→)")
    print("3. ขึ้น (↑)")
    print("4. ลง (↓)")
    while True:
        try:
            choice = int(input("เลือกทิศทาง (1-4): "))
            if choice < 1 or choice > 4:
                raise ValueError
            break
        except ValueError:
            print("กรุณากรอกตัวเลข 1-4 เท่านั้น!")
    return choice - 1

def check_cat_win():
    if catX == goalX and catY == goalY:
        print("แมวถึงจุดหมายแล้ว!")
        print("แมวชนะ!")
        return True

# -------------------- GAME LOOP --------------------
def game_loop():
    global catX, catY, dogX, dogY, gameOver
    global cat_can_phase_next, cat_phasing_active, cat_skip_turns

    base_map = get_map(level)
    spawn_items(base_map)  # ← สุ่มไอเทมตามกติกา

    while not gameOver:
        print_board(base_map)

        # ---------- เทิร์นของแมว ----------
        if cat_skip_turns > 0:
            cat_skip_turns -= 1
            print("\nแมวถูกโซ่ล็อก! ข้ามตานี้")
        else:
            # เปิดโหมดทะลุกำแพงถ้าคิวไว้จากตาที่แล้ว
            if cat_can_phase_next:
                cat_phasing_active = True
                cat_can_phase_next = False
                print("\n[แมว] ได้พลังปลา: ทะลุกำแพงได้ตานี้!")

            print("\nแมวกำลังเลือกทิศทาง...")
            cat_direction = choose_direction()
            cat_distance = random.randint(1, 4)
            print(f"แมวเดิน {cat_distance} ช่อง")
            cat_distance = int(input("แมวเดินกี่ช่อง? (test)"))

            for _ in range(cat_distance):
                new_catX = catX + dx[cat_direction]
                new_catY = catY + dy[cat_direction]
                if is_valid_move_cat(new_catX, new_catY, base_map):
                    catX, catY = new_catX, new_catY
                    # เช็คเก็บไอเทม (ของแมวเท่านั้น)
                    if (catX, catY) in cat_items:
                        cat_items.remove((catX, catY))
                        cat_can_phase_next = True
                        print("[แมว] เก็บปลา! ตาถัดไปทะลุกำแพงได้ 1 ตา")
                    # ของหมาเก็บไม่ได้
                else:
                    print("แมวติดกับกำแพง!")
                    break

            # หมดตาแล้วปิดโหมดทะลุกำแพง
            cat_phasing_active = False

        print_board(base_map)

        # ถ้าแมวเดินมาทับหมา -> โดน -1 ทันที
        gameOver = dog_attacks_cat()
        if gameOver: break

        # ตรวจว่าแมวชนะ
        gameOver = check_cat_win()
        if gameOver: break

        # ---------- เทิร์นของหมา ----------
        print("\nหมากำลังเลือกทิศทาง...")
        dog_direction = choose_direction()
        dog_distance = random.randint(1, 4)
        dog_distance = int(input("หมาเดินกี่ช่อง? (test)"))
        print(f"หมาเดิน {dog_distance} ช่อง")

        touched_cat_anytime = False
        for _ in range(dog_distance):
            new_dogX = dogX + dx[dog_direction]
            new_dogY = dogY + dy[dog_direction]
            if not is_valid_move_dog(new_dogX, new_dogY, base_map):
                print("หมาติดกับกำแพง!")
                break
            dogX, dogY = new_dogX, new_dogY

            # เก็บไอเทมของหมาได้เมื่อเดินผ่าน/ยืนทับ
            if (dogX, dogY) in dog_items:
                dog_items.remove((dogX, dogY))
                cat_skip_turns += 1
                print("[หมา] เก็บโซ่ล็อก! แมวจะถูกข้ามตาเพิ่ม 1")

            # ของแมาเก็บไม่ได้ (ปล่อยทิ้งไว้)
            if dogX == catX and dogY == catY:
                touched_cat_anytime = True

        # ตัดสินดาเมจจากตำแหน่งสุดท้ายจริง
        ended_on_cat = (dogX == catX and dogY == catY)
        if ended_on_cat and not gameOver:
            apply_cat_damage(1.0, "หมาทับแมวตอนจบเทิร์น!")
        elif touched_cat_anytime and not gameOver:
            apply_cat_damage(0.5, "หมาเดินผ่านแมวระหว่างทาง!")

# เริ่มเกม
game_loop()
print("จบเกม!")
