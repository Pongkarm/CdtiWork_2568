# a = "pop"

# print(a[::-1])



# import random

# def count_consecutive_ones(target=5):
#     count = 0
#     attempts = 0

#     while True:
#         a = random.randint(0, 1)
#         print(a)
#         if a == 1:
#             count += 1
#             if count == target:
#                 break
#         else:
#             count = 0
#             attempts += 1

#     return attempts

# attempts = count_consecutive_ones(10)
# print("Number of attempts before 5 consecutive 1s:", attempts)

# #write information at file a.txt
# with open('a.txt', 'a') as f:
#     f.write('Number of attempts before 5 consecutive 1s: '+ str(attempts)+"\n")


t = 100
sum = 0
count = 0
for i in range(t):
    sum += 1
    if '9' in '{:02d}'.format(i) or '4' in '{:02d}'.format(i) or '6' in '{:02d}'.format(i):
        continue
    print(i)
    count += 1
print(count)

# a = '{:02d}'.format(1)
# print(type(a))