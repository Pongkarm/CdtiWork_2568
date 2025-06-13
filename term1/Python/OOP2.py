# --- Base Item ---
class Item:
    def __init__(self, name):
        self.name = name

    def use(self, target):
        pass

# --- Potion ฟื้น HP ---
class Potion(Item):
    def __init__(self, name="Potion", heal_amount=30):
        super().__init__(name)
        self.heal_amount = heal_amount

    def use(self, target):
        target.hp = min(100, target.hp + self.heal_amount)
        print(f"{target.name} ใช้ {self.name} ฟื้น HP เป็น {target.hp}")

# --- ตัวละครหลัก ---
class Character:
    def __init__(self, name, level=1, exp=0, hp=100):
        self.name = name
        self.level = level
        self.exp = exp
        self.hp = hp
        self.inventory = []  # 💼 กระเป๋า

    def level_up(self):
        self.level += 1
        self.exp -= 100
        self.hp = 100
        print(f"{self.name} เลเวลอัปเป็น {self.level} แล้ว! ฟื้น HP เต็ม!")

    @property
    def status(self):
        return f"Name: {self.name}, Level: {self.level}, Exp: {self.exp}, HP: {self.hp}"

    def attack(self, target):
        if isinstance(target, Character) or isinstance(target, Enemy):
            target.hp -= 20
            print(f"{self.name} โจมตี {target.name}! HP ของ {target.name} เหลือ {target.hp}")
            if target.hp <= 0:
                print(f"{target.name} พ่ายแพ้แล้ว!")

    def use_item(self, item_name):
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                item.use(self)
                self.inventory.remove(item)
                return
        print(f"{self.name} ไม่มีไอเทมชื่อ {item_name}")

# --- อาชีพ Warrior ---
class Warrior(Character):
    def fight(self):
        if self.hp > 10:
            self.hp -= 10
            self.exp += 30
            print(f"{self.name} ต่อสู้แบบนักรบ! เหลือ HP {self.hp}")
            if self.exp >= 100:
                self.level_up()
        else:
            print(f"{self.name} หมดแรง ต้องพักก่อน")

# --- อาชีพ Mage ---
class Mage(Character):
    def cast_spell(self):
        if self.hp > 20:
            self.hp -= 20
            self.exp += 40
            print(f"{self.name} ร่ายเวทย์! เหลือ HP {self.hp}")
            if self.exp >= 100:
                self.level_up()
        else:
            print(f"{self.name} หมดพลังเวทย์ ต้องพักก่อน")

# --- ศัตรู Enemy ---
class Enemy:
    def __init__(self, name, hp=50):
        self.name = name
        self.hp = hp

    def attack(self, target):
        target.hp -= 15
        print(f"{self.name} โจมตี {target.name}! HP เหลือ {target.hp}")
        if target.hp <= 0:
            print(f"{target.name} พ่ายแพ้แล้ว!")

# --- ทดลองเล่น ---
if __name__ == "__main__":
    w = Warrior("Thorn")
    m = Mage("Zenya")
    enemy = Enemy("Slime King")

    potion = Potion()
    m.inventory.append(potion)
    m.inventory.append(potion)

    print(w.status)
    print(m.status)

    m.cast_spell()
    m.cast_spell()
    print(m.status)

    m.use_item("Potion")
    print(m.status)

    w.attack(enemy)
    enemy.attack(w)
    print(w.status)
