        .ORIG x3000

        LEA R1, SOURCE     ; R1 = base address ของ SOURCE
        LEA R2, DEST       ; R2 = base address ของ DEST
        LD  R3, LENGTH     ; R3 = ความยาว array (จำนวนสมาชิกที่จะ copy)

LOOP    LDR R4, R1, #0     ; โหลดค่าจาก memory[SOURCE] → R4
        STR R4, R2, #0     ; เก็บค่า R4 → memory[DEST]

        ADD R1, R1, #1     ; เลื่อนไปตำแหน่งถัดไปของ SOURCE
        ADD R2, R2, #1     ; เลื่อนไปตำแหน่งถัดไปของ DEST
        ADD R3, R3, #-1    ; ลดตัวนับลง 1
        BRp LOOP           ; ถ้า R3 > 0 ให้วน loop ต่อ

        HALT               ; จบโปรแกรม

; ----------------------------
SOURCE  .FILL #10           ; array[0] = 10
        .FILL #20           ; array[1] = 20
        .FILL #30           ; array[2] = 30
        .FILL #40           ; array[3] = 40
LENGTH  .FILL #4            ; จำนวนสมาชิก = 4

DEST    .BLKW #4            ; เว้นพื้นที่เก็บ array 4 ค่า

        .END
