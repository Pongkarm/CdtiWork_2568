import numpy as np
 
a = np.array([1, 2, 3])   # สร้าง array 1 มิติ
print(a)                  # [1 2 3]
print(a[0], a[1], a[2])   # 1 2 3
a[2] = 5                  # เปลี่ยนค่าใน array
print(a)                  # [1 2 5]
 
b = np.array([[1,2,3],[4,5,6]])    # สร้าง array 2 มิติ
print(b)                           # [[1 2 3]
                                  #  [4 5 6]]
 
# เราสามารถดูขนาดรูปร่างของ array ได้
print(a.shape)            # (3,)
print(b.shape)            # (2, 3)