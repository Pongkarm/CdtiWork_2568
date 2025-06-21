# x = 0
# y = 0
# z = 0

# for i in range(100):
#     if z == 2:
#         y += 1
#         z = 0
#         if y == 2:
#             x += 1
#             y = 0
#     if x == 2:
#         break
#     print(x, y, z)
#     z += 1
        



for x in range(2):
    for y in range(2):
        for z in range(2):
            print(x, y, z)
            print(not(not(x) or (x and y and z)))
            print(not(not((x or y) and (x and y and z))))
def generator_range(n):
    for i in range(n):
        yield i  # คืนทีละตัว

for num in generator_range(5):
    print(num)
# 0
# 1
# 2
# 3
# 4
