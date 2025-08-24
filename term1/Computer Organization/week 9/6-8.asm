        .ORIG   x3001

        ; ตั้งค่าตัวชี้ไปยังอาเรย์ A และ B
        LEA     R0, A          ; R0 = &A[0]  (x300E)
        LEA     R1, B          ; R1 = &B[0]  (x3013)

        ; โหลดตัวนับรอบ n
        AND     R2, R2, #0     ; เคลียร์ R2
        LD      R2, N          ; R2 = n (จาก x3018)

LOOP    LDR     R3, R0, #0     ; R3 = A[i]
        LDR     R4, R1, #0     ; R4 = B[i]
        ADD     R3, R3, R4     ; R3 = A[i] + B[i]
        STR     R3, R0, #0     ; A[i] = ผลรวม

        ADD     R0, R0, #1     ; ชี้ไปสมาชิกถัดไปของ A
        ADD     R1, R1, #1     ; ชี้ไปสมาชิกถัดไปของ B
        ADD     R2, R2, #-1    ; ลดตัวนับ
        BRp     LOOP           ; ถ้า R2 > 0 ให้ลูปต่อ

        TRAP    x25            ; HALT

; -------- ข้อมูล --------
A       .FILL   #5
        .FILL   #4
        .FILL   #3
        .FILL   #6
        .FILL   #2

B       .FILL   #4
        .FILL   #7
        .FILL   #6
        .FILL   #8
        .FILL   #7

N       .FILL   #5

        .END
