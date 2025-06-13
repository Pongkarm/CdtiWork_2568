# import random
# import datetime
# time = datetime.datetime.now().microsecond

# def generate_lottery_number():
#     return "{:06d}".format(random.randint(0, 999999))

# # สุ่มรางวัลที่ 1 ขึ้นมาก่อน
# winning_number = generate_lottery_number()
# print(f"รางวัลที่ 1 คือ: {winning_number}")

# attempts = 0
# while True:
#     attempts += 1
#     ticket = generate_lottery_number()
#     if ticket == winning_number:
#         print(f"ถูกรางวัลที่ 1 หลังจากซื้อไปทั้งหมด {attempts} ใบ")
#         break
# with open('b.txt', 'a') as f:
#     f.write(f"ถูกรางวัลที่ 1 หลังจากซื้อไปทั้งหมด {attempts} ใบ\n")
import sys
sys.setrecursionlimit(10000)  # หรือมากกว่านี้ตามที่ต้องการ

a = [4, 6, 7, 9]
print(a[:])