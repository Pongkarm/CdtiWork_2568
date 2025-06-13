class BankAccount:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
    def deposit(self, amount):
        self.balance += amount
    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
        elif self.balance <= 0:
            print("เงินในบัญชีของคุณไม่พอ")
    def get_balance(self):
        return self.balance
acc = BankAccount("Alice", 1000)
acc.deposit(500)
acc.withdraw(300)
print(acc.get_balance())  # 1200

class Pet:
    def __init__(self, name):
        self.name = name
    def sound(self):
        pass
class Dog(Pet):
    def __init__(self, name):
        super().__init__(name)
    @property
    def sound(self):
        print("เห่า Woof!")
    @property
    def sound2(self):
        print("hong")
class Cat(Pet):
    def __init__(self, name):
        super().__init__(name)
    @property
    def sound(self):
        print("เหมียว Meow!") 

dog = Dog("Buddy")
cat = Cat("Mimi")

dog.sound  # เห่า: Woof!
cat.sound  # เหมียว: Meow!
