        .ORIG x3000

; --- Load inputs ---
        LDI   R0, DIVD_PTR   ; R0 <- A = M[x4000] (dividend)
        LDI   R1, DIVS_PTR     ; R1 <- B = M[x4001] (divisor)

; --- Handle B == 0 (หลีกเลี่ยงหารด้วยศูนย์) ---
        AND   R2, R2, #0       ; R2 = Q = 0
        ADD   R3, R0, #0       ; R3 = R = A (เผื่อกรณีหารด้วยศูนย์ก็เก็บ A เป็น remainder)
        BRz   DIV_BY_ZERO      ; ถ้า R1 (B) == 0 -> เก็บผลแล้วจบ

; --- Prepare loop variables ---
        NOT   R5, R1           ; R5 = ~B
        ADD   R5, R5, #1       ; R5 = -B

; --- Repeated subtraction loop: while (R - B) >= 0 ---
LOOP    ADD   R4, R3, R5      ; R4 = R - B (ทดลองลบ)
        BRn   DONE             ; ถ้า < 0 ออกลูป
        ADD   R3, R3, R5       ; R = R - B
        ADD   R2, R2, #1       ; Q++
        BRnzp LOOP

; --- Write outputs (ปกติ) ---
DONE    STI   R2, Q_PTR        ; M[x5000] <- Q
        STI   R3, R_PTR        ; M[x5001] <- R
        HALT

; --- Write outputs (B == 0) ---
DIV_BY_ZERO
        STI   R2, Q_PTR        ; Q = 0
        STI   R3, R_PTR        ; R = A
        HALT

; --- Pointers for LDI/STI ---
DIVD_PTR .FILL x4000           ; address of dividend
DIVS_PTR .FILL x4001           ; address of divisor
Q_PTR    .FILL x5000           ; address to store quotient
R_PTR    .FILL x5001           ; address to store remainder

        .END
        
.ORIG   x4000
        .FILL   #17 
        .FILL   #5        
        .END
