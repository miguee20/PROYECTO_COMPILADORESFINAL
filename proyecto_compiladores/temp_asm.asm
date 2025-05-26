; Código generado automáticamente desde C
.MODEL SMALL
.STACK 100H
.DATA
    x DW 0
    y DW 0
    msg_0 DB "negativo$"
    msg_1 DB "entre 1 y 9$"
    msg_2 DB "demasiado grande$"

.CODE
MAIN PROC
    MOV AX, @DATA
    MOV DS, AX
    MOV x, 5
    LEA DX, msg_0
    MOV AH, 09H
    INT 21H
    LEA DX, msg_1
    MOV AH, 09H
    INT 21H
    LEA DX, msg_2
    MOV AH, 09H
    INT 21H

    MOV AH, 4CH
    INT 21H
MAIN ENDP
END MAIN