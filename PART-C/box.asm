
// Make the Computer Draw a Box
// K = 76
// Width = 16 pixels
// Height = 20 rows
// Starting row = 76

(START)
    @KBD
    D=M
    @DRAW
    D;JNE

// Clear the box when no key is pressed

(CLEAR)
    @SCREEN
    D=A
    @2432
    D=D+A
    @R13
    M=D

    @20
    D=A
    @R14
    M=D

(CLEAR_LOOP)
    @R13
    A=M
    M=0

    @R13
    D=M
    @32
    D=D+A
    @R13
    M=D

    @R14
    MD=M-1
    @CLEAR_LOOP
    D;JGT

    @START
    0;JMP

// Draw the black box when a key is pressed

(DRAW)
    @SCREEN
    D=A
    @2432
    D=D+A
    @R13
    M=D

    @20
    D=A
    @R14
    M=D

(DRAW_LOOP)
    @R13
    A=M
    M=-1

    @R13
    D=M
    @32
    D=D+A
    @R13
    M=D

    @R14
    MD=M-1
    @DRAW_LOOP
    D;JGT

    @START
    0;JMP