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

    # Medidas básicas de cada bloque
    ANCHO, ALTO = 100, 50
    SESGO = 15        # “Inclinación” del paralelogramo (cuánto se desplaza la esquina)

    for bloque in diagrama:
        x, y   = bloque.x, bloque.y
        tipo   = bloque.tipo.lower()   # normalizamos a minúsculas

        # INICIO / FIN  → óvalo
        if tipo in ("inicio", "fin"):
            bloque.canvas_id = canvas.create_oval(
                x, y, x + ANCHO, y + ALTO,
                fill="lightblue"
            )

        # PROCESO → rectángulo
        elif tipo == "proceso":
            bloque.canvas_id = canvas.create_rectangle(
                x, y, x + ANCHO, y + ALTO,
                fill="lightgreen"
            )

        # ENTRADA / SALIDA → paralelogramo
        elif tipo in ("entrada", "salida", "entrada/salida"):
            bloque.canvas_id = canvas.create_polygon(
                x + SESGO, y,                 # vértice superior izquierdo “desplazado”
                x + ANCHO, y,                # vértice superior derecho
                x + ANCHO - SESGO, y + ALTO, # vértice inferior derecho “desplazado hacia la izquierda”
                x, y + ALTO,                 # vértice inferior izquierdo
                fill="plum1"
            )

        # DECISIÓN → rombo
        elif tipo == "decisión":
            bloque.canvas_id = canvas.create_polygon(
                x + ANCHO / 2, y,                 # punta superior
                x + ANCHO,     y + ALTO / 2,      # punta derecha
                x + ANCHO / 2, y + ALTO,          # punta inferior
                x,             y + ALTO / 2,      # punta izquierda
                fill="gold"
            )

        # Otros tipos → rectángulo gris claro (fallback)
        else:
            bloque.canvas_id = canvas.create_rectangle(
                x, y, x + ANCHO, y + ALTO,
                fill="gray85"
            )

        # Texto centrado dentro de la figura
        texto = bloque.contenido or bloque.tipo.upper()
        bloque.text_id = canvas.create_text(
            x + ANCHO / 2, y + ALTO / 2,
            text=texto,
            font=("Arial", 9, "bold")
        )

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
    global puerto_origen, linea_temporal, arrastrando_desde_puerto, bloque_seleccionado, conexiones

    arrastrando_desde_puerto = False

    if linea_temporal:
        canvas.delete(linea_temporal)
        linea_temporal = None

    # Obtener posición de release
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    
    # Buscar bloque destino
    bloque_destino = None
    for bloque in diagrama:
        if bloque.x <= x <= bloque.x + 100 and bloque.y <= y <= bloque.y + 50:
            bloque_destino = bloque
            break

    # Si hay un bloque seleccionado y un destino válido
    if bloque_seleccionado and bloque_destino and bloque_seleccionado != bloque_destino:
        # Para bloques de decisión
        if bloque_seleccionado.tipo == "decisión":
            # Pedir tipo de conexión (Sí/No)
            tipo = simpledialog.askstring("Tipo de conexión", "Ingrese 'si' o 'no' para la conexión:")
            if tipo and tipo.lower() in ['si', 'no']:
                # Verificar si ya existe una conexión del mismo tipo
                existe_conexion = any(
                    c.origen == bloque_seleccionado and c.tipo == tipo 
                    for c in conexiones
                )
                
                if not existe_conexion:
                    conexion = Conexion(bloque_seleccionado, bloque_destino, tipo)
                    conexiones.append(conexion)
                else:
                    tk.messagebox.showerror("Error", f"Ya existe una conexión '{tipo}' para este bloque de decisión")
        else:
            # Para otros bloques (conexión normal)
            conexion = Conexion(bloque_seleccionado, bloque_destino, 'normal')
            conexiones.append(conexion)
        
        # Actualizar visualización
        dibujar_bloques()
        mostrar_diagrama()

    # Limpiar selección
    puerto_origen = None
    bloque_seleccionado = None

def generar_codigo_c():
    codigo = "#include <stdio.h>\n\nint main() {\n"
    indent = "    "
    variables_declaradas = set()
    pila_estructuras = []  # Para manejar anidamiento
    bloques_procesados = set()

    def declarar_variable(var):
        nonlocal codigo
        if var not in variables_declaradas and var.isidentifier():
            codigo += f"{indent * len(pila_estructuras)}int {var};\n"
            variables_declaradas.add(var)

    def detectar_for(bloque, i, conexiones):
        # El bloque debe ser una decisión tipo "i < n"
        if bloque.tipo != "decisión" or i < 1:
            return False

        init_bloque = diagrama[i - 1]
        if init_bloque.tipo != "proceso":
            return False

        init_contenido = init_bloque.contenido.replace(" ", "")
        if "=" not in init_contenido:
            return False

        var_init, val_init = init_contenido.split("=")
        var = var_init.strip()

        # Verifica que en la conexión "no" haya un incremento de la misma variable
        for c in conexiones:
            if c.origen == bloque and c.tipo == "no":
                destino = c.destino
                if destino.tipo == "proceso":
                    contenido = destino.contenido.replace(" ", "")
                    if contenido.startswith(f"{var}=") and (
                        "+1" in contenido or "++" in contenido
                    ):
                        return True
        return False



    i = 0
    while i < len(diagrama):
        bloque = diagrama[i]
        if bloque in bloques_procesados:
            i += 1
            continue
            
        bloques_procesados.add(bloque)
        indent_actual = indent * len(pila_estructuras)

        # --- BLOQUES BÁSICOS ---
        if bloque.tipo == "inicio":
            pass
        elif bloque.tipo == "entrada":
            declarar_variable(bloque.contenido)
            codigo += f"{indent_actual}scanf(\"%d\", &{bloque.contenido});\n"
        elif bloque.tipo == "proceso":
            # Optimizar i = i + 1 → i++
            contenido = bloque.contenido.replace(" ", "")
            if contenido.endswith("=i+1") or contenido.endswith("+=1"):
                var = contenido.split("=")[0]
                codigo += f"{indent_actual}{var}++;\n"
            else:
                codigo += f"{indent_actual}{bloque.contenido};\n"
        elif bloque.tipo == "salida":
            codigo += f"{indent_actual}printf(\"%d\\n\", {bloque.contenido});\n"
        elif bloque.tipo == "fin":
            codigo += f"{indent_actual}return 0;\n"
            
        # --- ESTRUCTURAS DE CONTROL ---
        elif bloque.tipo == "decisión":
            condicion = bloque.contenido

            # Detectar FOR
            if detectar_for(bloque, i, conexiones):
                init_bloque = diagrama[i - 1]
                var, val = init_bloque.contenido.replace(" ", "").split("=")
                codigo += f"{indent_actual}for ({var} = {val}; {condicion}; {var}++) {{\n"
                pila_estructuras.append("for")
                bloques_procesados.add(diagrama[i - 1])  # i = 0
                # Bloque de incremento (como i++)
                for conexion in conexiones:
                    if conexion.origen == bloque and conexion.tipo == "no":
                        bloques_procesados.add(conexion.destino)
                i += 1  # Saltar el init_bloque ya procesado

            # Detectar WHILE (si hay conexión "si" hacia atrás)
            elif any(
                c.tipo == "si" and diagrama.index(c.destino) < i
                for c in conexiones if c.origen == bloque
            ):
                codigo += f"{indent_actual}while ({condicion}) {{\n"
                pila_estructuras.append("while")

            # IF normal
            else:
                codigo += f"{indent_actual}if ({condicion}) {{\n"
                pila_estructuras.append("if")

                for conexion in [c for c in conexiones if c.origen == bloque and c.tipo == "si"]:
                    if conexion.destino.tipo in ["proceso", "salida"]:
                        codigo += f"{indent_actual}    {conexion.destino.contenido};\n"
                    bloques_procesados.add(conexion.destino)

                codigo += f"{indent_actual}}} else {{\n"

                for conexion in [c for c in conexiones if c.origen == bloque and c.tipo == "no"]:
                    if conexion.destino.tipo in ["proceso", "salida"]:
                        codigo += f"{indent_actual}    {conexion.destino.contenido};\n"
                    bloques_procesados.add(conexion.destino)

                codigo += f"{indent_actual}}}\n"
                pila_estructuras.pop()


        # Cierre de estructuras
        # Cierre de estructuras si no hay continuación lógica
        proximos = [c.destino for c in conexiones if c.origen == bloque]
        if not proximos or (i + 1 < len(diagrama) and diagrama[i + 1] not in proximos):
            while pila_estructuras:
                estructura = pila_estructuras.pop()
                codigo += f"{indent * len(pila_estructuras)}}}\n"


        i += 1

    # Declarar variables no inicializadas
    vars_usadas = set()
    for bloque in diagrama:
        if bloque.contenido:
            for token in bloque.contenido.replace(";", "").split():
                if token.isidentifier() and token not in ["printf", "scanf"]:
                    vars_usadas.add(token)
    
    declaraciones = ""
    for var in vars_usadas:
        if var not in variables_declaradas:
            declaraciones += f"{indent}int {var};\n"
    
    codigo = codigo.replace("#include <stdio.h>\n\nint main() {\n", 
                        f"#include <stdio.h>\n\nint main() {{\n{declaraciones}")

    return codigo
def mostrar_codigo_c(codigo):
    ventana_c = Toplevel()
    ventana_c.title("Código en C")
    ventana_c.geometry("600x400")
    texto_c = scrolledtext.ScrolledText(ventana_c, font=("Courier", 10), bg="black", fg="lime", insertbackground="white")
    texto_c.pack(fill="both", expand=True)
    texto_c.insert(tk.END, codigo)

def on_generar_c_click():
    try:
        if not diagrama:
            raise ValueError("El diagrama está vacío")
        
        codigo = generar_codigo_c()
        if not codigo.strip():
            raise ValueError("No se generó código válido")
            
        mostrar_codigo_c(codigo)
    except Exception as e:
        ventana_error = Toplevel()
        ventana_error.title("Error")
        ventana_error.geometry("300x100")
        tk.Label(ventana_error, text=f"Error al generar código:\n{str(e)}", fg="red").pack()

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
    archivo = filedialog.asksaveasfilename(
        defaultextension=".json", 
        filetypes=[("Diagrama de flujo", "*.json"), ("Todos los archivos", "*.*")]
    )
    if not archivo:
        return
    
    try:
        # Preparar datos de bloques
        bloques_data = []
        for bloque in diagrama:
            bloque_data = {
                "tipo": bloque.tipo,
                "contenido": bloque.contenido,
                "x": bloque.x,
                "y": bloque.y,
                "canvas_id": None,  # No guardamos IDs del canvas
                "text_id": None     # No guardamos IDs de texto
            }
            bloques_data.append(bloque_data)
        
        # Preparar datos de conexiones
        conexiones_data = []
        for conexion in conexiones:
            try:
                origen_idx = diagrama.index(conexion.origen)
                destino_idx = diagrama.index(conexion.destino)
                conexiones_data.append({
                    "origen": origen_idx,
                    "destino": destino_idx,
                    "tipo": conexion.tipo
                })
            except ValueError:
                continue  # Si no encuentra el bloque, omite la conexión
        
        # Estructura completa del archivo
        data = {
            "version": 1.0,
            "bloques": bloques_data,
            "conexiones": conexiones_data
        }
        
        # Guardar con formato legible
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        tk.messagebox.showinfo("Éxito", "Diagrama guardado correctamente")
        
    except Exception as e:
        tk.messagebox.showerror("Error", f"No se pudo guardar el diagrama:\n{str(e)}")

def cargar_diagrama():
    global diagrama, conexiones
    
    archivo = filedialog.askopenfilename(
        defaultextension=".json", 
        filetypes=[("Diagrama de flujo", "*.json"), ("Todos los archivos", "*.*")]
    )
    if not archivo:
        return
    
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validar estructura básica
        if not isinstance(data, dict) or "bloques" not in data:
            raise ValueError("El archivo no tiene un formato válido")
        
        # Limpiar diagrama actual
        diagrama.clear()
        conexiones.clear()
        
        # Cargar bloques
        for b_data in data["bloques"]:
            bloque = Bloque(b_data["tipo"], b_data.get("contenido"))
            bloque.x = b_data.get("x", 100)
            bloque.y = b_data.get("y", 100)
            diagrama.append(bloque)
        
        # Cargar conexiones (si existen en el archivo)
        if "conexiones" in data:
            for c_data in data["conexiones"]:
                try:
                    origen = diagrama[c_data["origen"]]
                    destino = diagrama[c_data["destino"]]
                    conexion = Conexion(origen, destino, c_data["tipo"])
                    conexiones.append(conexion)
                except (IndexError, KeyError):
                    continue  # Omite conexiones inválidas
        
        # Reconstruir relaciones si/no para decisiones (para compatibilidad con versiones antiguas)
        if "conexiones" not in data:
            for bloque in diagrama:
                if bloque.tipo == "decisión" and not bloque.si and not bloque.no:
                    bloque.si.append(Bloque('proceso', 'Bloque SI'))
                    bloque.no.append(Bloque('proceso', 'Bloque NO'))
        
        dibujar_bloques()
        mostrar_diagrama()
        tk.messagebox.showinfo("Éxito", "Diagrama cargado correctamente")
        
    except json.JSONDecodeError:
        tk.messagebox.showerror("Error", "El archivo no es un JSON válido")
    except Exception as e:
        tk.messagebox.showerror("Error", f"No se pudo cargar el diagrama:\n{str(e)}")
        # Limpiar en caso de error parcial
        diagrama.clear()
        conexiones.clear()
        dibujar_bloques()

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

btn_c = tk.Button(ventana, text="Generar C", command=on_generar_c_click, bg="gold", fg="black", font=("Arial", 10, "bold"))
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


