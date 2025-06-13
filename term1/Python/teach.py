#ข้อ 1
def is_palindrome(word):
    _len = (len(word)//2)
    for i in range(1,_len+1):
        if word[i-1] == word[-i]:
            continue
        return False
    return True

print(is_palindrome("po554op"))
#แบบเกทับ
# def is_palindrome(word):
#     n = len(word)
#     for i in range(n // 2):
#         if word[i] != word[n - i - 1]:
#             return False
#     return True
#แบบพระเจ้า
# def is_palindrome(word):
#     return word == word[::-1]

#ข้อ 2
# def find_mode(number):
#     count_best = 0
#     for i in range(len(number)):
#         count = 0
#         for a in number:
#             if a == number[i]:
#                 count += 1
#         if count > count_best:
#             count_best = count
#             answer = i
#     return number[answer]
# question = [1, 3, 5, 3, 5, 6, 8, 9, 5, 7, 3, 3, 3, 8, 8, 8, 8, 8]
# answer = find_mode(question)
# print(answer)

#เกทับ
def find_mode(numbers):
    freq = {}
    max_count = 0
    mode = None
    for num in numbers:
        freq[num] = freq.get(num, 0) + 1
        if freq[num] > max_count:
            max_count = freq[num]
            mode = num
    return mode


#ข้อ 3
#ทำไม่เป็นกรุณาอ่อนโยนด้วย
def caesar_cipher(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - base + shift) % 26
            result += chr(base + shifted)
        else:
            result += char
    return result

print(caesar_cipher("Hello World!", 3))  # Khoor Zruog!

#ข้อ 4
# def split_string(string):
#     for i in string:
#         if i == ' ':
#             print(' ', end="")
#         print(i, end="")
# split_string("12345 6789 ")
#ผิดไอ้ควาย ดูของจริง
def manual_split(sentence):
    result = []
    word = ""
    for char in sentence:
        if char == " ":
            if word != "":
                result.append(word)
                word = ""
        else:
            word += char
    if word:  # เผื่อคำสุดท้ายไม่ตามด้วย space
        result.append(word)
    return result

print(manual_split("hello world python is fun"))
# ['hello', 'world', 'python', 'is', 'fun']


#ข้อ 5
#ทำไม่เป็นกรุณาอ่อนโยนด้วย