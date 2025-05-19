import tkinter as tk
from tkinter import simpledialog, Toplevel, scrolledtext

# Clase para los bloques
class Bloque:
    def __init__(self, tipo, contenido=None):
        self.tipo = tipo
        self.contenido = contenido
        self.si = []
        self.no = []

    def __str__(self):
        if self.tipo == 'decisión':
            si_str = '\n'.join(['    SI: ' + str(b) for b in self.si])
            no_str = '\n'.join(['    NO: ' + str(b) for b in self.no])
            return f"DECISIÓN: {self.contenido}\n{si_str}\n{no_str}"
        elif self.tipo in ['proceso', 'entrada', 'salida']:
            return f"{self.tipo.upper()}: {self.contenido}"
        else:
            return f"{self.tipo.upper()}"

# Lista del diagrama
diagrama = []

# Función para agregar bloques
def agregar_bloque(tipo):
    if tipo in ['entrada', 'proceso', 'salida', 'decisión']:
        contenido = simpledialog.askstring("Contenido", f"Ingrese el contenido del bloque '{tipo}':")
        if contenido:
            bloque = Bloque(tipo, contenido)
            if tipo == 'decisión':
                bloque.si.append(Bloque('proceso', 'Bloque SI'))
                bloque.no.append(Bloque('proceso', 'Bloque NO'))
            diagrama.append(bloque)
    else:
        diagrama.append(Bloque(tipo))
    mostrar_diagrama()

# Mostrar el contenido del diagrama
def mostrar_diagrama():
    texto.delete(1.0, tk.END)
    for bloque in diagrama:
        texto.insert(tk.END, str(bloque) + '\n\n')

# Función que genera código en C
def generar_codigo_c():
    codigo = "#include <stdio.h>\n\nint main() {\n"
    indent = "    "
    for bloque in diagrama:
        if bloque.tipo == "inicio":
            continue
        elif bloque.tipo == "entrada":
            codigo += f"{indent}int {bloque.contenido};\n"
            codigo += f"{indent}scanf(\"%d\", &{bloque.contenido});\n"
        elif bloque.tipo == "proceso":
            codigo += f"{indent}{bloque.contenido};\n"
        elif bloque.tipo == "salida":
            codigo += f"{indent}printf(\"%d\\n\", {bloque.contenido});\n"
        elif bloque.tipo == "decisión":
            codigo += f"{indent}if ({bloque.contenido}) {{\n"
            for si_bloque in bloque.si:
                if si_bloque.tipo == "proceso":
                    codigo += f"{indent*2}{si_bloque.contenido};\n"
                elif si_bloque.tipo == "salida":
                    codigo += f"{indent*2}printf(\"%d\\n\", {si_bloque.contenido});\n"
            codigo += f"{indent}}} else {{\n"
            for no_bloque in bloque.no:
                if no_bloque.tipo == "proceso":
                    codigo += f"{indent*2}{no_bloque.contenido};\n"
                elif no_bloque.tipo == "salida":
                    codigo += f"{indent*2}printf(\"%d\\n\", {no_bloque.contenido});\n"
            codigo += f"{indent}}}\n"
        elif bloque.tipo == "fin":
            codigo += f"{indent}return 0;\n"

    codigo += "}\n"
    mostrar_codigo_c(codigo)

# Mostrar el código C en una nueva ventana
def mostrar_codigo_c(codigo):
    ventana_c = Toplevel()
    ventana_c.title("Código en C")
    ventana_c.geometry("600x400")
    texto_c = scrolledtext.ScrolledText(ventana_c, font=("Courier", 10), bg="black", fg="lime", insertbackground="white")
    texto_c.pack(fill="both", expand=True)
    texto_c.insert(tk.END, codigo)


# Función para generar el codigo ensamblador ASM
def generar_codigo_asm():
    asm = ".MODEL SMALL\n.STACK 100H\n.DATA\n"
    usados = []

    # Crear secciones de datos (para variables)
    for bloque in diagrama:
        if bloque.tipo == "entrada":
            if bloque.contenido not in usados:
                asm += f"    {bloque.contenido} DB 0\n"
                usados.append(bloque.contenido)
        elif bloque.tipo == "salida":
            if bloque.contenido not in usados:
                asm += f"    {bloque.contenido} DB 0\n"
                usados.append(bloque.contenido)

    asm += ".CODE\nMAIN:\n"
    asm += "    MOV AX, @DATA\n    MOV DS, AX\n"

    for bloque in diagrama:
        if bloque.tipo == "entrada":
            asm += f"    ; Leer {bloque.contenido}\n"
            asm += "    ; Simulación de lectura - reemplazar según necesidad\n"
            asm += f"    MOV {bloque.contenido}, 5 ; Valor fijo como ejemplo\n"
        elif bloque.tipo == "proceso":
            asm += f"    ; {bloque.contenido}\n"
        partes = bloque.contenido.replace(" ", "").split("=")
        if len(partes) == 2:
            var_dest = partes[0]
            expresion = partes[1]

            if "+" in expresion:
                op1, op2 = expresion.split("+")
                asm += f"    MOV AL, {op1}\n"
                asm += f"    ADD AL, {op2}\n"
                asm += f"    MOV {var_dest}, AL\n"
            elif "-" in expresion:
                op1, op2 = expresion.split("-")
                asm += f"    MOV AL, {op1}\n"
                asm += f"    SUB AL, {op2}\n"
                asm += f"    MOV {var_dest}, AL\n"
            elif "*" in expresion:
                op1, op2 = expresion.split("*")
                asm += f"    MOV AL, {op1}\n"
                asm += f"    MOV BL, {op2}\n"
                asm += f"    MUL BL\n"               # Resultado en AX
                asm += f"    MOV {var_dest}, AL\n"   # Guardamos solo la parte baja
            elif "/" in expresion:
                op1, op2 = expresion.split("/")
                asm += f"    MOV AL, {op1}\n"
                asm += f"    CBW\n"                  # Sign extension
                asm += f"    MOV BL, {op2}\n"
                asm += f"    DIV BL\n"
                asm += f"    MOV {var_dest}, AL\n"
            else:
                # Asignación directa
                asm += f"    MOV AL, {expresion}\n"
                asm += f"    MOV {var_dest}, AL\n"


        elif bloque.tipo == "salida":
            asm += f"    ; Mostrar {bloque.contenido}\n"
            asm += "    MOV DL, '0' + {0}\n".format(bloque.contenido)
            asm += "    MOV AH, 02H\n    INT 21H\n"
        elif bloque.tipo == "decisión":
            asm += f"    ; Evaluar condición: {bloque.contenido}\n"
            asm += "    ; Simulación de condición\n"
            asm += "    CMP AL, BL\n    JE etiqueta_si\n    JMP etiqueta_no\n"
            asm += "etiqueta_si:\n"
            for si_bloque in bloque.si:
                asm += f"    ; {si_bloque.tipo.upper()}: {si_bloque.contenido}\n"
            asm += "    JMP fin_decision\n"
            asm += "etiqueta_no:\n"
            for no_bloque in bloque.no:
                asm += f"    ; {no_bloque.tipo.upper()}: {no_bloque.contenido}\n"
            asm += "fin_decision:\n"
        elif bloque.tipo == "fin":
            asm += "    MOV AH, 4CH\n    INT 21H\n"

    asm += "END MAIN\n"
    mostrar_codigo_asm(asm)

def mostrar_codigo_asm(codigo):
    ventana_asm = Toplevel()
    ventana_asm.title("Código Ensamblador")
    ventana_asm.geometry("600x400")
    texto_asm = scrolledtext.ScrolledText(ventana_asm, font=("Courier", 10), bg="black", fg="lightgreen", insertbackground="white")
    texto_asm.pack(fill="both", expand=True)
    texto_asm.insert(tk.END, codigo)


# Interfaz principal
ventana = tk.Tk()
ventana.title("Generador de Diagrama de Flujo")
ventana.geometry("700x520")
ventana.configure(bg="midnight blue")

btn_style = {"bg": "slategray2", "fg": "black", "font": ("Arial", 10, "bold"), "relief": "groove", "width": 12}

# Botones de bloques
tipos = ['inicio', 'entrada', 'proceso', 'decisión', 'salida', 'fin']
for i, tipo in enumerate(tipos):
    b = tk.Button(ventana, text=tipo.upper(), command=lambda t=tipo: agregar_bloque(t), **btn_style)
    b.grid(row=0, column=i, padx=5, pady=10)



# Botón para generar C
btn_generar_c = tk.Button(ventana, text="Generar Código C", command=generar_codigo_c, bg="gold", fg="black", font=("Arial", 10, "bold"))
btn_generar_c.grid(row=1, column=0, columnspan=6, pady=5)

# Botón para generar ensamblador
btn_generar_asm = tk.Button(ventana, text="Generar Código ASM", command=generar_codigo_asm, bg="orange", fg="black", font=("Arial", 10, "bold"))
btn_generar_asm.grid(row=3, column=0, columnspan=6, pady=5)


# Caja de texto con el diagrama
texto = tk.Text(ventana, width=80, height=23, bg="black", fg="gold", font=("Courier", 10))
texto.grid(row=2, column=0, columnspan=6, padx=10, pady=10)

ventana.mainloop()


