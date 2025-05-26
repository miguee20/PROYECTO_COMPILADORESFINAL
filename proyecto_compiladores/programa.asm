.MODEL SMALL
.STACK 100H
.DATA
    x DB 0
    msg_0 DB "entre 1 y 9$"
    msg_1 DB "demasiado grande$"
    msg_2 DB "negativo$"
.CODE
MAIN:
    MOV AX, @DATA
    MOV DS, AX
ETQ_0:
    JMP ETQ_1
ETQ_1:
    MOV x, 5 ; entrada fija
    JMP ETQ_2
ETQ_2:
    MOV AL, x
    CMP AL, 0
    JG ETQ_3
    JMP ETQ_6
ETQ_3:
    MOV AL, x
    CMP AL, 10
    JL ETQ_4
    JMP ETQ_5
ETQ_4:
    LEA DX, msg_0
    MOV AH, 09H
    INT 21H
    JMP ETQ_7
ETQ_5:
    LEA DX, msg_1
    MOV AH, 09H
    INT 21H
    JMP ETQ_7
ETQ_6:
    LEA DX, msg_2
    MOV AH, 09H
    INT 21H
    JMP ETQ_7
ETQ_7:
FIN:
    MOV AH, 4CH
    INT 21H
END MAIN
