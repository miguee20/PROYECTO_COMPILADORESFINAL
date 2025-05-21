import tkinter as tk
from tkinter import simpledialog, Toplevel, scrolledtext

# Clase para los bloques
class Bloque:
    def __init__(self, tipo, contenido=None):
        self.tipo = tipo
        self.contenido = contenido
        self.si = []
        self.no = []
        self.x = 100
        self.y = 100
        self.canvas_id = None
        self.text_id = None

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
        if not contenido:
            return
        bloque = Bloque(tipo, contenido)
        if tipo == 'decisión':
            bloque.si.append(Bloque('proceso', 'Bloque SI'))
            bloque.no.append(Bloque('proceso', 'Bloque NO'))
    else:
        bloque = Bloque(tipo)

    bloque.x = 100 + len(diagrama) * 150
    bloque.y = 150
    diagrama.append(bloque)
    dibujar_bloques()
    mostrar_diagrama()

def dibujar_bloques():
    canvas.delete("all")
    for i, bloque in enumerate(diagrama):
        x, y = bloque.x, bloque.y
        if bloque.tipo == 'inicio' or bloque.tipo == 'fin':
            bloque.canvas_id = canvas.create_oval(x, y, x+100, y+50, fill="lightblue")
        elif bloque.tipo == 'decisión':
            bloque.canvas_id = canvas.create_polygon(
                x+50, y,
                x+100, y+25,
                x+50, y+50,
                x, y+25,
                fill="gold"
            )
        else:
            bloque.canvas_id = canvas.create_rectangle(x, y, x+100, y+50, fill="lightgreen")

        texto = bloque.tipo.upper() if not bloque.contenido else bloque.contenido
        bloque.text_id = canvas.create_text(x+50, y+25, text=texto, font=("Arial", 9, "bold"))

        if i > 0:
            x1, y1 = diagrama[i-1].x+50, diagrama[i-1].y+50
            x2, y2 = bloque.x+50, bloque.y
            canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST)

# Mostrar el contenido del diagrama
def mostrar_diagrama():
    texto.delete(1.0, tk.END)
    for bloque in diagrama:
        texto.insert(tk.END, str(bloque) + '\n\n')

# Función para limpiar todo
def limpiar_diagrama():
    diagrama.clear()
    canvas.delete("all")
    texto.delete(1.0, tk.END)

# Funciones para mover bloques con el mouse
moviendo_bloque = None
def on_canvas_click(event):
    global moviendo_bloque
    click_x = canvas.canvasx(event.x)
    click_y = canvas.canvasy(event.y)
    for bloque in diagrama:
        x1, y1 = bloque.x, bloque.y
        x2, y2 = x1 + 100, y1 + 50
        if x1 <= click_x <= x2 and y1 <= click_y <= y2:
            moviendo_bloque = bloque
            break

def on_canvas_drag(event):
    global moviendo_bloque
    if moviendo_bloque:
        mouse_x = canvas.canvasx(event.x)
        mouse_y = canvas.canvasy(event.y)
        moviendo_bloque.x = mouse_x - 50
        moviendo_bloque.y = mouse_y - 25
        dibujar_bloques()

def on_canvas_release(event):
    global moviendo_bloque
    moviendo_bloque = None

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

def mostrar_codigo_c(codigo):
    ventana_c = Toplevel()
    ventana_c.title("Código en C")
    ventana_c.geometry("600x400")
    texto_c = scrolledtext.ScrolledText(ventana_c, font=("Courier", 10), bg="black", fg="lime", insertbackground="white")
    texto_c.pack(fill="both", expand=True)
    texto_c.insert(tk.END, codigo)

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

# --- Interfaz principal ---
ventana = tk.Tk()
ventana.title("Editor de Diagrama de Flujo")
ventana.geometry("950x600")
ventana.configure(bg="midnight blue")

# Botones de bloques
btn_style = {"bg": "slategray2", "fg": "black", "font": ("Arial", 10, "bold"), "relief": "groove", "width": 10}
tipos = ['inicio', 'entrada', 'proceso', 'decisión', 'salida', 'fin']
for i, tipo in enumerate(tipos):
    b = tk.Button(ventana, text=tipo.upper(), command=lambda t=tipo: agregar_bloque(t), **btn_style)
    b.place(x=10 + i*110, y=10)

# Botón para limpiar todo
btn_clear = tk.Button(ventana, text="Limpiar Todo", command=limpiar_diagrama, bg="red", fg="white", font=("Arial", 10, "bold"))
btn_clear.place(x=10, y=50)

# Canvas para dibujo
canvas = tk.Canvas(ventana, width=700, height=400, bg="white")
canvas.place(x=10, y=100)
canvas.bind("<Button-1>", on_canvas_click)
canvas.bind("<B1-Motion>", on_canvas_drag)
canvas.bind("<ButtonRelease-1>", on_canvas_release)


# Texto del diagrama
texto = tk.Text(ventana, width=35, height=30, bg="black", fg="gold", font=("Courier", 9))
texto.place(x=730, y=10)

# --- Frame con Scroll para el Canvas ---
canvas_frame = tk.Frame(ventana, width=700, height=400)
canvas_frame.place(x=10, y=100)

scroll_y = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

scroll_x = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

canvas = tk.Canvas(canvas_frame, width=680, height=380, bg="white",
                   yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                   scrollregion=(0, 0, 2000, 2000))  # Puedes ajustar el tamaño del área de trabajo aquí

scroll_y.config(command=canvas.yview)
scroll_x.config(command=canvas.xview)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Eventos de movimiento de bloques (sin cambios)
canvas.bind("<Button-1>", on_canvas_click)
canvas.bind("<B1-Motion>", on_canvas_drag)
canvas.bind("<ButtonRelease-1>", on_canvas_release)

# Zoom con Ctrl + Rueda del mouse
scale = 1.0

def zoom(event):
    global scale
    if event.state & 0x0004:  # Ctrl presionado
        if event.delta > 0:
            factor = 1.1
        else:
            factor = 0.9
        scale *= factor
        canvas.scale("all", canvas.canvasx(event.x), canvas.canvasy(event.y), factor, factor)
        canvas.configure(scrollregion=canvas.bbox("all"))

canvas.bind("<MouseWheel>", zoom)  # Para Windows
canvas.bind("<Button-4>", zoom)    # Para Linux (scroll up)
canvas.bind("<Button-5>", zoom)    # Para Linux (scroll down)

ventana.mainloop()
