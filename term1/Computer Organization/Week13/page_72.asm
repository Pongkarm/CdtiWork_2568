.ORIG X4000
PROMPT
    TRAP x20
    STR R0, R1, #0
    ADD R1, R1, #1
    ADD R0, R0, #-10
    BRnp PROMPT
END
    ADD R1, R1, #-1
    STR R0, R1, #0
    LEA R0, INPUT
    
    TRAP x22
    TRAP x25
    
INPUT .BLKW 64
.END