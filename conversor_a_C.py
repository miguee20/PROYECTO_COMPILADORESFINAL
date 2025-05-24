import tkinter as tk
from tkinter import simpledialog, Toplevel, scrolledtext
import pickle
from tkinter import filedialog
import json

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
        

class Conexion:
    def __init__(self, origen, destino, tipo):
        self.origen = origen
        self.destino = destino
        self.tipo = tipo  # 'si' o 'no'
        self.line_id = None
        self.text_id = None

# Lista del diagrama
diagrama = []
arrastrando_desde_puerto = False

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

        # Dibujar puertos solo si el bloque está seleccionado
    if bloque_seleccionado:
        for dx, dy in [(50, 0), (50, 50), (0, 25), (100, 25)]:  # arriba, abajo, izquierda, derecha
            px, py = bloque_seleccionado.x + dx, bloque_seleccionado.y + dy
            r = 5
            canvas.create_oval(px - r, py - r, px + r, py + r, fill="black", tags=("puerto",))
        # Dibujar conexiones manuales
    for conexion in conexiones:
        # Punto de partida
        if conexion.origen.tipo == "inicio":
            x1 = conexion.origen.x + 50  # centro horizontal
            y1 = conexion.origen.y + 50  # parte inferior
        elif conexion.origen.tipo == "decisión":
            if conexion.tipo == "si":
                x1 = conexion.origen.x + 100  # lado derecho
                y1 = conexion.origen.y + 25   # centro vertical
            elif conexion.tipo == "no":
                x1 = conexion.origen.x + 50   # centro horizontal
                y1 = conexion.origen.y + 50   # parte inferior
            else:
                x1 = conexion.origen.x + 50
                y1 = conexion.origen.y + 50
        else:
            x1 = conexion.origen.x + 50
            y1 = conexion.origen.y + 50

        # Punto final
        # Punto final (posición de entrada al destino)
        if conexion.tipo == "si":
            x2 = conexion.destino.x  # lado izquierdo
            y2 = conexion.destino.y + 25  # centro vertical
        else:
            x2 = conexion.destino.x + 50  # centro horizontal
            y2 = conexion.destino.y       # parte superior


        # Color y texto
        color = "green" if conexion.tipo == "si" else "red" if conexion.tipo == "no" else "blue"
        label = "Sí" if conexion.tipo == "si" else "No" if conexion.tipo == "no" else ""

        # Dibujar la línea y el texto
        conexion.line_id = canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill=color, width=2)
        if label:
            conexion.text_id = canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2 - 10, text=label, fill=color, font=("Arial", 9, "bold"))


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

bloque_seleccionado = None
puerto_origen = None
linea_temporal = None
conexiones = []  # Lista de tuplas (bloque_origen, bloque_destino)

# Funciones para mover bloques con el mouse
moviendo_bloque = None
def on_canvas_click(event):
    global moviendo_bloque, bloque_seleccionado, arrastrando_desde_puerto

    if arrastrando_desde_puerto:
        return  # Evitar mover bloques si estamos arrastrando desde un puerto

    click_x = canvas.canvasx(event.x)
    click_y = canvas.canvasy(event.y)
    bloque_seleccionado = None
    moviendo_bloque = None

    for bloque in diagrama:
        x1, y1 = bloque.x, bloque.y
        x2, y2 = x1 + 100, y1 + 50
        if x1 <= click_x <= x2 and y1 <= click_y <= y2:
            moviendo_bloque = bloque
            bloque_seleccionado = bloque
            break

    dibujar_bloques()


def on_canvas_drag(event):
    global moviendo_bloque
    if moviendo_bloque:
        mouse_x = canvas.canvasx(event.x)
        mouse_y = canvas.canvasy(event.y)
        moviendo_bloque.x = mouse_x - 50
        moviendo_bloque.y = mouse_y - 25
        dibujar_bloques()

def on_canvas_release(event):
    global moviendo_bloque, arrastrando_desde_puerto
    moviendo_bloque = None
    arrastrando_desde_puerto = False

def on_puerto_click(event):
    global puerto_origen, linea_temporal, arrastrando_desde_puerto
    arrastrando_desde_puerto = True
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    puerto_origen = (x, y)
    linea_temporal = canvas.create_line(x, y, x, y, arrow=tk.LAST, dash=(4, 2))

def on_puerto_drag(event):
    global linea_temporal
    if linea_temporal:
        x2, y2 = canvas.canvasx(event.x), canvas.canvasy(event.y)
        canvas.coords(linea_temporal, puerto_origen[0], puerto_origen[1], x2, y2)

def on_puerto_release(event):
    global puerto_origen, linea_temporal, arrastrando_desde_puerto

    arrastrando_desde_puerto = False

    if linea_temporal:
        canvas.delete(linea_temporal)
        linea_temporal = None

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    for bloque in diagrama:
        if bloque.x <= x <= bloque.x + 100 and bloque.y <= y <= bloque.y + 50:
            if bloque_seleccionado and bloque != bloque_seleccionado:
                if bloque_seleccionado.tipo == "decisión":
                    tipo = simpledialog.askstring("Tipo", "¿'si' o 'no'?")
                    if tipo in ['si', 'no']:
                        conexiones.append(Conexion(bloque_seleccionado, bloque, tipo))
                else:
                    conexiones.append(Conexion(bloque_seleccionado, bloque, 'normal'))

    puerto_origen = None
    dibujar_bloques()


def generar_codigo_c():
    codigo = "#include <stdio.h>\n\nint main() {\n"
    indent = "    "
    variables_declaradas = set()

    for bloque in diagrama:
        if bloque.tipo == "inicio":
            continue
        elif bloque.tipo == "entrada":
            if bloque.contenido not in variables_declaradas:
                codigo += f"{indent}int {bloque.contenido};\n"
                variables_declaradas.add(bloque.contenido)
            codigo += f"{indent}scanf(\"%d\", &{bloque.contenido});\n"
        elif bloque.tipo == "proceso":
            codigo += f"{indent}{bloque.contenido};\n"
        elif bloque.tipo == "salida":
            codigo += f"{indent}printf(\"%d\\n\", {bloque.contenido});\n"
        elif bloque.tipo == "decisión":
            condicion = bloque.contenido.strip()
            if any(op in condicion for op in ['<', '>', '==', '!=', '<=', '>=']):
                codigo += f"{indent}if ({condicion}) {{\n"
            else:
                codigo += f"{indent}// Revisa esta condición: {condicion}\n"
                codigo += f"{indent}if ({condicion}) {{\n"

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

def guardar_diagrama():
    archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Diagrama de flujo", "*.json")])
    if archivo:
        data = []
        for b in diagrama:
            bloque_data = {
                "tipo": b.tipo,
                "contenido": b.contenido,
                "x": b.x,
                "y": b.y,
                "si": [diagrama.index(s) for s in b.si],
                "no": [diagrama.index(n) for n in b.no]
            }
            data.append(bloque_data)
        with open(archivo, "w") as f:
            json.dump(data, f, indent=4)
def cargar_diagrama():
    global diagrama
    archivo = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Diagrama de flujo", "*.json")])
    if archivo:
        with open(archivo, "r") as f:
            data = json.load(f)

        diagrama.clear()
        for b in data:
            bloque = Bloque(b["tipo"], b["contenido"])
            bloque.x = b["x"]
            bloque.y = b["y"]
            diagrama.append(bloque)

        # Reconectar relaciones
        for i, b in enumerate(data):
            diagrama[i].si = [diagrama[j] for j in b["si"]]
            diagrama[i].no = [diagrama[j] for j in b["no"]]

        dibujar_bloques()
        mostrar_diagrama()


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

# Botón para limpiar todo, guardar, cargar, generar c y generar asm
btn_clear = tk.Button(ventana, text="Limpiar Todo", command=limpiar_diagrama, bg="red", fg="white", font=("Arial", 10, "bold"))
btn_clear.place(x=10, y=50)

btn_guardar = tk.Button(ventana, text="Guardar", command=guardar_diagrama, bg="green", fg="white", font=("Arial", 10, "bold"))
btn_guardar.place(x=130, y=50)

btn_cargar = tk.Button(ventana, text="Cargar", command=cargar_diagrama, bg="blue", fg="white", font=("Arial", 10, "bold"))
btn_cargar.place(x=230, y=50)

btn_c = tk.Button(ventana, text="Generar C", command=generar_codigo_c, bg="gold", fg="black", font=("Arial", 10, "bold"))
btn_c.place(x=350, y=50)

btn_asm = tk.Button(ventana, text="Generar ASM", command=generar_codigo_asm, bg="orange", fg="black", font=("Arial", 10, "bold"))
btn_asm.place(x=470, y=50)


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
canvas.tag_bind("puerto", "<Button-1>", on_puerto_click)
canvas.tag_bind("puerto", "<B1-Motion>", on_puerto_drag)
canvas.tag_bind("puerto", "<ButtonRelease-1>", on_puerto_release)



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


