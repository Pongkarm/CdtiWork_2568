        .ORIG   x3000

        AND     R1, R1, #0      ; R1 = 0
        ADD     R1, R1, #15     ; R1 = 15 (นับจำนวนบิต)

        LDI     R2, DATA_PTR    ; โหลดข้อมูลจากหน่วยความจำไป R2

CHK1    BRn     DONE            ; ถ้า bit15 ของ R2 = 1 -> หยุด

        ADD     R1, R1, #-1     ; R1--
        BRn     EXIT            ; ถ้า R1 < 0 -> หมดแล้ว -> ออกเลย

        ADD     R2, R2, R2      ; shift-left 1 บิต
        BRn     DONE            ; ถ้า bit15 = 1 -> หยุด
        BRnzp   CHK1            ; ไม่งั้นวนต่อ

DONE    HALT
EXIT    HALT

DATA_PTR .FILL  x3100           ; ชี้ไปยังข้อมูล 1 คำ
        .END

  
        .ORIG   x3100
        .FILL   x0001          ; หรือเปลี่ยนเป็นค่าที่ต้องการตรวจ
        .END
