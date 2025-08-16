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

print(max(100, 200, 300))

import random
count1 = 0
# สุ่มการออกไอเทมสองกล่องกล่องแรกโอการ 1.1% กล่องสอง 1.85%
while True:
    item1 = random.randint(1, 1000)
    if item1 <= 11:
        print("ไอเทมสองกล่องแรก")
        print(count1)
        print(count1/5)
        break
    count1 += 1

count2 = 0
while True:
    item2 = random.randint(1, 1000)
    if item2 <= 18:
        print("ไอเทมสองกล่องสอง")
        print(count2)
        print(count2/5)
        break
    count2 += 1
#เปิดกล่องแรกดีกว่า หลอกกูนะเกมเหี้ย