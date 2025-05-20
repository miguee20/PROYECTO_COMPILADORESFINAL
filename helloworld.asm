section .data 
    msg db "Hello world", 0Ah 

section .text
    global _start
_start
    ;----------------- imprimir print(msg) ---------------------
    mov edx, 12 ; longitud de cadena
    mov ecx, msg ; cadena a imprimir
    mov ebx, 1 ; tipo de salida (STDOUT file)
    mov eax, 4 ; SYS_WRITE (kernel opocode)
    int 80h 
       
    ;-------------------- end ----------------------------
    mov ebx, 0  ; return 0 status on exit 
    mov eax, 1 ; SYS_EXIT (kernel opocode 1)
    int 80h
