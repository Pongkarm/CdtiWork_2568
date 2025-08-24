;     .ORIG x3000

;         LDI     R1, SEC_NUM
;         LDI     R2, FRS_NUM 

;         AND     R0, R0, #0      ; set 0
;         AND     R4, R4, #0      ; set 0
;         AND     R5, R5, #0
;         NOT     R4, R2          ; R4 = -R2
;         ADD     R4, R4, #1
;         ADD     R5, R1, R4      ; R5 = R1 - R2
        
;         BRn     LESS            ; if negative → R1 < R2
;         BRp     GREATER         ; if positive → R1 > R2
;         BRz     EQUAL           ; if zero → R1 = R2

; EQUAL   AND     R0, R0, #0      ; R0 = 0
;         BRnzp   DONE

; GREATER ADD     R0, R0, #1      ; R0 = 1
;         BRnzp   DONE

; LESS    ADD     R0, R0, #-1     ; R0 = -1

; DONE    HALT


; ; ---------------------------------
; ; ---------------------------------


; FRS_NUM .FILL x3100
; SEC_NUM .FILL x3101

; .END

;         .ORIG x3100
;         .FILL #7
;         .FILL #5

;         .END



; UPGRAT




; Efficient Integer Multiply (result in R3)
; ใช้แนวคิดจาก 6.4 (เทียบสองจำนวน) + 6.5 (บวกซ้ำอย่างมีประสิทธิภาพ)

        .ORIG   x3000

;--- Load inputs ---
        LDI     R1, FRS_NUM        ; R1 <- first number (A)
        LDI     R2, SEC_NUM        ; R2 <- second number (B)

;--- Quick zero check ---
        AND     R3, R3, #0         ; R3 = 0 (default result)
        ADD     R4, R1, #0
        BRz     DONE               ; ถ้า A == 0 ให้ result = 0 เลย
        ADD     R4, R2, #0
        BRz     DONE               ; ถ้า B == 0 ให้ result = 0 เลย

;--- Determine sign and take absolute values ---

        AND     R6, R6, #0         ; R6 = sign flag count (0,1,2)

; abs(R1)
        ADD     R4, R1, #0
        BRzp    R1_POS
        NOT     R1, R1
        ADD     R1, R1, #1         ; R1 = |R1|
        ADD     R6, R6, #1         ; flipped sign once
R1_POS
; abs(R2)
        ADD     R4, R2, #0
        BRzp    R2_POS
        NOT     R2, R2
        ADD     R2, R2, #1         ; R2 = |R2|
        ADD     R6, R6, #1         ; flipped sign twice total?
R2_POS

;--- Choose direction: add larger number, fewer times ---
; compare R1 ? R2  (compute R5 = R1 - R2)
        NOT     R4, R2
        ADD     R4, R4, #1         ; R4 = -R2
        ADD     R5, R1, R4         ; R5 = R1 - R2
        BRn     R1_LT_R2           ; if R1 < R2

; R1 >= R2: multiplicand = R1 (R0), counter = R2 (R4)
        ADD     R0, R1, #0         ; R0 = M (bigger abs)
        ADD     R4, R2, #0         ; R4 = CNT (smaller abs)
        BRnzp   START_LOOP

R1_LT_R2
; R1 < R2: multiplicand = R2 (R0), counter = R1 (R4)
        ADD     R0, R2, #0         ; R0 = M
        ADD     R4, R1, #0         ; R4 = CNT

;--- Repeated addition loop: R3 = CNT * M ---
        AND     R3, R3, #0         ; R3 = 0

START_LOOP
        ADD     R5, R4, #0
        BRz     LOOP_END           ; while CNT > 0
        ADD     R3, R3, R0         ; R3 += M
        ADD     R4, R4, #-1        ; CNT--
        BRnzp   START_LOOP

LOOP_END
;--- Apply sign if signs differed (R6 == 1) ---
        ADD     R5, R6, #-1
        BRz     NEGATE             ; if R6 == 1 -> negate result
        BRnzp   DONE

NEGATE  NOT     R3, R3
        ADD     R3, R3, #1

DONE    HALT

;-------------------------------
; Pointers to input data
;-------------------------------
FRS_NUM .FILL   x3100
SEC_NUM .FILL   x3101

        .END

;-------------------------------
; Example data (editable)
;-------------------------------
        .ORIG   x3100
        .FILL   #7          ; first  number A
        .FILL   #-5         ; second number B
        .END
