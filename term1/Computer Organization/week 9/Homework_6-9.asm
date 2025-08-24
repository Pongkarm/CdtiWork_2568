        .ORIG x3000

        LD      R1, COUNT     ; R1 = 100 (ตัวนับรอบ)
        LD      R0, CH_Z      ; R0 = 'Z' (ASCII x005A)

LOOP    TRAP    x21           ; OUT -> แสดงอักขระใน R0 ('Z')
        ADD     R1, R1, #-1   ; ตัวนับลดลง 1
        BRp     LOOP          ; ถ้ายัง > 0 ให้พิมพ์ต่อ

        HALT

COUNT   .FILL   #100          ; ค่าตัวนับเริ่มต้น = 100
CH_Z    .FILL   x005A         ; Z

        .END
