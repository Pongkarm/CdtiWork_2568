#แปลงจากฐาน 10 เป็นฐาน 2

def convert_to_binary(num):
    binary = ""
    while num > 0:
        remainder = num % 2
        binary = str(remainder) + binary
        num //= 2
    return binary

number = int(5)
binary = convert_to_binary(number)
print("Binary representation:", binary)

# a = 24.5235663675475554356
# b = 44.359883748957389573987598325453
# for i in range(10000):
#     a = a * b
#     b = b / a
#     print(a, b)

base = 2
num = '1101'
value = 0
a = 0
for i in num[::-1]:
    if i != '0':
        value += int(i)*(base**a)
    a+=1

print(value)
print(int('1101',2))
    
#print a to 2 decimal places
print(f"{6.625+0.025:.50f}")