

# class Character:
#     def __init__(self, name, level=1, exp=0, hp=100):
#         self.name = name
#         self.level = level
#         self.exp = exp
#         self.hp = hp

#     @property
#     def status(self):
#         return f"Name: {self.name}, Level: {self.level}, Exp: {self.exp} HP: {self.hp}"

# class Warrior(Character):
#     def __init__(self, name, level=1, exp=0 , hp=100):
#         super().__init__(name, level, exp , hp)

#     def fight(self):
#         if (self.hp - 10) >= 1:
#             self.hp -= 10
#             self.exp += 30
#             if self.exp >= 100:
#                 self.level += 1
#                 self.hp = 100
#                 self.exp -= 100
# class Mage(Character):
#     def __init__(self, name, level=1, exp=0 , hp=100):
#         super().__init__(name, level, exp , hp)

#     def cast_spell(self):
#         if (self.hp - 20) >= 1:
#             self.hp -= 20
#             self.exp += 40
#             if self.exp >= 100:
#                 self.level += 1
#                 self.hp = 100
#                 self.exp -= 100

# if __name__ == "__main__":
#     # ทดสอบ
#     w = Warrior("Thorn")
#     m = Mage("Zenya")

#     w.fight()
#     w.fight()
#     print(w.status)  # HP เหลือ 80

#     m.cast_spell()
#     m.cast_spell()
#     m.cast_spell()
#     print(m.status)  # เลเวลอัป, HP กลับเป็น 100
    
class Character:
    def __init__(self, name, level=1, exp=0, hp=100):
        self.name = name
        self.level = level
        self.exp = exp
        self.hp = hp

    def level_up(self):
        self.level += 1
        self.exp -= 100
        self.hp = 100
        print(f"{self.name} เลเวลอัปเป็น {self.level} แล้ว! ฟื้น HP เต็ม!")

    @property
    def status(self):
        return f"Name: {self.name}, Level: {self.level}, Exp: {self.exp}, HP: {self.hp}"


class Warrior(Character):
    def fight(self):
        if self.hp > 10:
            self.hp -= 10
            self.exp += 30
            if self.exp >= 100:
                self.level_up()
        else:
            print(f"{self.name} หมดแรงต่อสู้ ต้องพักก่อน!")


class Mage(Character):
    def cast_spell(self):
        if self.hp > 20:
            self.hp -= 20
            self.exp += 40
            if self.exp >= 100:
                self.level_up()
        else:
            print(f"{self.name} หมดพลังเวทย์ ต้องพักก่อน!")


# ทดสอบ
if __name__ == "__main__":
    w = Warrior("Thorn")
    m = Mage("Zenya")

    w.fight()
    w.fight()
    print(w.status)

    m.cast_spell()
    m.cast_spell()
    m.cast_spell()
    print(m.status)
