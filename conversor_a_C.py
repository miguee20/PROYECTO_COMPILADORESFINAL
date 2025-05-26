import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog, Toplevel, scrolledtext
import pickle
from tkinter import filedialog
import json
import os
import subprocess
import tempfile
import sys
import re


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


    # Modifica esta parte en dibujar_bloques():
    if bloque == bloque_seleccionado:
        # Dibujar borde resaltado
        canvas.create_rectangle(
            x-3, y-3, x + ANCHO+3, y + ALTO+3,
            outline="blue", width=3, dash=(3,3)
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
    
    # Verificar si es doble clic (edición)
    if event.num == 1 and event.type == tk.EventType.ButtonPress and event.time - getattr(on_canvas_click, 'last_click', 0) < 300:
        editar_bloque()
        on_canvas_click.last_click = 0
        return
    
    on_canvas_click.last_click = event.time
    
    # Resto del código original...
    if arrastrando_desde_puerto:
        return
    
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
    pila_estructuras = []
    bloques_procesados = set()

    def declarar_variable(var):
        nonlocal codigo
        if var not in variables_declaradas and var.isidentifier():
            codigo += f"{indent}int {var};\n"
            variables_declaradas.add(var)

    def detectar_for(bloque, i, conexiones):
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

        # Buscar la conexión 'si' (cuerpo del bucle)
        destino_si = next((c.destino for c in conexiones if c.origen == bloque and c.tipo == "si"), None)
        if not destino_si:
            return False

        # Buscar dentro de la rama 'si' si hay un incremento del tipo i++ o i = i + 1
        def contiene_incremento(bloque_actual, visitados=set()):
            if bloque_actual in visitados:
                return False
            visitados.add(bloque_actual)

            if bloque_actual.tipo == "proceso":
                if bloque_actual.contenido is None:
                    return False
                contenido = bloque_actual.contenido.replace(" ", "")
                if contenido == f"{var}++" or contenido == f"{var}+=1":
                    return True

            # Seguir por las conexiones salientes normales
            siguientes = [c.destino for c in conexiones if c.origen == bloque_actual and c.tipo == "normal"]
            return any(contiene_incremento(b, visitados) for b in siguientes)

        return contiene_incremento(destino_si)

    i = 0
    while i < len(diagrama):
        bloque = diagrama[i]
        if bloque in bloques_procesados:
            i += 1
            continue
        bloques_procesados.add(bloque)

        if bloque.tipo == "inicio":
            pass

        elif bloque.tipo == "entrada":
            contenido = bloque.contenido.strip()
            if "=" in contenido:
                var, val = contenido.replace(" ", "").split("=")
                declarar_variable(var)
                codigo += f"{indent}{var} = {val};\n"
            else:
                declarar_variable(contenido)
                codigo += f"{indent}scanf(\"%d\", &{contenido});\n"

        elif bloque.tipo == "proceso":
            if bloque.contenido is None:
                continue
            contenido = bloque.contenido.replace(" ", "")
            if any(op in contenido for op in ["=", "+=", "-="]):
                if "+1" in contenido or "++" in contenido:
                    var = contenido.split("=")[0]
                    if not (pila_estructuras and pila_estructuras[-1] == "for" and f"{var}++" in contenido):
                        codigo += f"{indent}{var}++;\n"
                else:
                    codigo += f"{indent}{bloque.contenido};\n"
            else:
                codigo += f"{indent}{bloque.contenido};\n"

        elif bloque.tipo == "salida":
            codigo += f"{indent}printf(\"%d\\n\", {bloque.contenido});\n"

        elif bloque.tipo == "fin":
            while pila_estructuras:
                codigo += f"{indent}}}\n"
                pila_estructuras.pop()
            codigo += f"{indent}return 0;\n"

        elif bloque.tipo == "decisión":
            condicion = bloque.contenido.strip()

            # Detectar for
            if detectar_for(bloque, i, conexiones):
                init_bloque = diagrama[i - 1]
                var, val = init_bloque.contenido.replace(" ", "").split("=")
                codigo += f"{indent}for ({var} = {val}; {condicion}; {var}++) {{\n"
                pila_estructuras.append("for")
                bloques_procesados.add(init_bloque)
                bloques_procesados.add(bloque)

                # También marcar como procesado el bloque que contiene el incremento
                destino_si = next((c.destino for c in conexiones if c.origen == bloque and c.tipo == "si"), None)
                if destino_si:
                    siguientes = [c.destino for c in conexiones if c.origen == destino_si and c.tipo == "normal"]
                    for b in siguientes:
                        if b.tipo == "proceso" and b.contenido.replace(" ", "") in [f"{var}++", f"{var}={var}+1"]:
                            bloques_procesados.add(b)

                i += 1
                continue

            # Detectar while solo si hay una conexión que vuelve hacia atrás
            # Detectar while si hay una conexión que regresa al mismo bloque de decisión
            es_while = any(
                c.destino == bloque and diagrama.index(c.origen) > i
                for c in conexiones if c.tipo == "normal"
            )


            if es_while:
                codigo += f"{indent}while ({condicion}) {{\n"
                pila_estructuras.append("while")
                continue

            # IF con posible anidamiento
            else:
                codigo += f"{indent}if ({condicion}) {{\n"
                pila_estructuras.append("if")

                for c in [c for c in conexiones if c.origen == bloque and c.tipo == "si"]:
                    if c.destino.tipo in ["proceso", "salida"]:
                        codigo += f"{indent*2}{c.destino.contenido};\n"
                        bloques_procesados.add(c.destino)

                codigo += f"{indent}}} else {{\n"

                for c in [c for c in conexiones if c.origen == bloque and c.tipo == "no"]:
                    if c.destino.tipo in ["proceso", "salida"]:
                        codigo += f"{indent*2}{c.destino.contenido};\n"
                        bloques_procesados.add(c.destino)

                codigo += f"{indent}}}\n"
                pila_estructuras.pop()
                continue

        proximos = [c.destino for c in conexiones if c.origen == bloque]
        if not proximos or (i + 1 < len(diagrama) and diagrama[i + 1] not in proximos):
            while pila_estructuras:
                codigo += f"{indent}}}\n"
                pila_estructuras.pop()

        i += 1

    vars_usadas = set()
    for bloque in diagrama:
        if bloque.contenido:
            for token in bloque.contenido.replace(";", "").replace("=", " ").replace("+", " ").replace("-", " ").split():
                if token.isidentifier() and token not in ["printf", "scanf"]:
                    vars_usadas.add(token)

    declaraciones = ""
    for var in vars_usadas:
        if var not in variables_declaradas:
            declaraciones += f"{indent}int {var};\n"

    codigo = codigo.replace("int main() {\n", f"int main() {{\n{declaraciones}")
    codigo += "}\n"
    return codigo

def mostrar_codigo_c(codigo):
    ventana_c = Toplevel()
    ventana_c.title("Código en C")
    ventana_c.geometry("600x400")
    texto_c = scrolledtext.ScrolledText(ventana_c, font=("Courier", 10), bg="black", fg="lime", insertbackground="white")
    texto_c.pack(fill="both", expand=True)
    texto_c.insert(tk.END, codigo)


def mostrar_salida_ejecucion(salida):
    ventana_salida = Toplevel()
    ventana_salida.title("Salida del programa")
    ventana_salida.geometry("600x300")
    texto_salida = scrolledtext.ScrolledText(ventana_salida, font=("Courier", 10), bg="black", fg="lime", insertbackground="white")
    texto_salida.pack(fill="both", expand=True)
    texto_salida.insert(tk.END, salida)


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
    variables = set()
    mensajes = []
    etiquetas = {}
    asm_instrucciones = []

    def detectar_for_asm(i):
        if i < 2:
            return False
        bloque_decision = diagrama[i]
        bloque_init = diagrama[i - 2]
        bloque_incremento = diagrama[i + 1] if i + 1 < len(diagrama) else None

        if not (bloque_decision.tipo == "decisión" and
                bloque_init.tipo == "proceso" and
                bloque_incremento and bloque_incremento.tipo == "proceso"):
            return False

        cond = bloque_decision.contenido.replace(" ", "")
        if "<" not in cond and "<=" not in cond:
            return False
        var_cond = cond.split("<")[0] if "<" in cond else cond.split("<=")[0]
        var_cond = var_cond.strip()

        inc_text = bloque_incremento.contenido.replace(" ", "")
        return inc_text in [f"{var_cond}++", f"{var_cond}+=1", f"{var_cond}={var_cond}+1"]

    for i, bloque in enumerate(diagrama):
        etiquetas[bloque] = f"ETQ_{i}"

    for bloque in diagrama:
        if bloque.contenido:
            if bloque.tipo in ["entrada", "proceso"]:
                contenido = bloque.contenido.replace(" ", "")
                if "=" in contenido:
                    var = contenido.split("=")[0]
                    if var.isidentifier():
                        variables.add(var)
            if "printf" in bloque.contenido:
                msg_text = bloque.contenido.strip()
                msg_clean = msg_text.replace("printf(", "").replace(")", "").replace('"', '').strip()
                label = f"msg_{len(mensajes)}"
                mensajes.append((bloque, label, msg_clean))

    for var in variables:
        asm += f"    {var} DB 0\n"
    for _, label, contenido in mensajes:
        asm += f"    {label} DB \"{contenido}$\"\n"

    asm += ".CODE\nMAIN:\n"
    asm += "    MOV AX, @DATA\n    MOV DS, AX\n"

    for i, bloque in enumerate(diagrama):
        asm_instrucciones.append(f"{etiquetas[bloque]}:")

        if bloque.tipo == "entrada" and bloque.contenido:
            var, val = bloque.contenido.replace(" ", "").split("=")
            asm_instrucciones.append(f"    MOV {var}, {val} ; entrada fija")

        elif bloque.tipo == "proceso" and bloque.contenido:
            contenido = bloque.contenido.strip()
            if "printf" in contenido:
                tokens = contenido.replace("printf(", "").replace(")", "").split(",")
                mensaje = tokens[0].replace('"', '').strip()
                var_impresa = tokens[1].strip() if len(tokens) > 1 else None
                for b, label, msg in mensajes:
                    if msg == mensaje:
                        asm_instrucciones.append(f"    LEA DX, {label}")
                        asm_instrucciones.append(f"    MOV AH, 09H")
                        asm_instrucciones.append(f"    INT 21H")
                        break
                if var_impresa:
                    asm_instrucciones.append(f"    MOV AL, {var_impresa}")
                    asm_instrucciones.append(f"    ADD AL, 30h")
                    asm_instrucciones.append(f"    MOV DL, AL")
                    asm_instrucciones.append(f"    MOV AH, 02H")
                    asm_instrucciones.append(f"    INT 21H")
                    asm_instrucciones.append(f"    MOV DL, 13")
                    asm_instrucciones.append(f"    MOV AH, 02H")
                    asm_instrucciones.append(f"    INT 21H")
                    asm_instrucciones.append(f"    MOV DL, 10")
                    asm_instrucciones.append(f"    MOV AH, 02H")
                    asm_instrucciones.append(f"    INT 21H")
            elif contenido.endswith("++") or "+=1" in contenido:
                var = contenido.replace("++", "").replace("+=1", "").strip()
                asm_instrucciones.append(f"    MOV AL, {var}")
                asm_instrucciones.append(f"    INC AL")
                asm_instrucciones.append(f"    MOV {var}, AL")
            elif "=" in contenido:
                var_dest, expr = contenido.split("=")
                var_dest = var_dest.strip()
                expr = expr.strip()
                if "+" in expr:
                    op1, op2 = expr.split("+")
                    asm_instrucciones.append(f"    MOV AL, {op1.strip()}")
                    asm_instrucciones.append(f"    ADD AL, {op2.strip()}")
                    asm_instrucciones.append(f"    MOV {var_dest}, AL")
                elif "-" in expr:
                    op1, op2 = expr.split("-")
                    asm_instrucciones.append(f"    MOV AL, {op1.strip()}")
                    asm_instrucciones.append(f"    SUB AL, {op2.strip()}")
                    asm_instrucciones.append(f"    MOV {var_dest}, AL")
                else:
                    asm_instrucciones.append(f"    MOV {var_dest}, {expr}")

        elif bloque.tipo == "salida" and bloque.contenido:
            for b, label, msg in mensajes:
                if b == bloque:
                    asm_instrucciones.append(f"    LEA DX, {label}")
                    asm_instrucciones.append(f"    MOV AH, 09H")
                    asm_instrucciones.append(f"    INT 21H")
                    break

        elif bloque.tipo == "decisión" and bloque.contenido:
            condicion = bloque.contenido.replace(" ", "")
            operadores = {">": "JG", "<": "JL", ">=": "JGE", "<=": "JLE", "==": "JE", "!=": "JNE"}
            operador_encontrado = next((op for op in sorted(operadores, key=lambda x: -len(x)) if op in condicion), None)

            if operador_encontrado:
                var, val = condicion.split(operador_encontrado)
                var = var.strip()
                val = val.strip()
                destino_si = next((c.destino for c in conexiones if c.origen == bloque and c.tipo == "si"), None)
                destino_no = next((c.destino for c in conexiones if c.origen == bloque and c.tipo == "no"), None)

                if detectar_for_asm(i):
                    asm_instrucciones.append(f"    JMP {etiquetas[bloque]}_COND")
                    if destino_si:
                        asm_instrucciones.append(f"{etiquetas[destino_si]}:")
                    siguiente = next((c.destino for c in conexiones if c.origen == destino_si and c.tipo == "normal"), None)
                    if siguiente:
                        asm_instrucciones.append(f"    JMP {etiquetas[bloque]}_COND")
                    asm_instrucciones.append(f"{etiquetas[bloque]}_COND:")
                    asm_instrucciones.append(f"    MOV AL, {var}")
                    asm_instrucciones.append(f"    CMP AL, {val}")
                    asm_instrucciones.append(f"    {operadores[operador_encontrado]} {etiquetas[destino_si]}")
                    asm_instrucciones.append(f"    JMP {etiquetas[destino_no]}")
                    continue

                es_while = any(c.destino == bloque and diagrama.index(c.origen) > i for c in conexiones if c.tipo == "normal")
                if es_while:
                    asm_instrucciones.append(f"{etiquetas[bloque]}_WHILE:")
                    asm_instrucciones.append(f"    MOV AL, {var}")
                    asm_instrucciones.append(f"    CMP AL, {val}")
                    asm_instrucciones.append(f"    {operadores[operador_encontrado]} {etiquetas[destino_si]}")
                    asm_instrucciones.append(f"    JMP {etiquetas[destino_no]}")
                    continue

                asm_instrucciones.append(f"    MOV AL, {var}")
                asm_instrucciones.append(f"    CMP AL, {val}")
                asm_instrucciones.append(f"    {operadores[operador_encontrado]} {etiquetas[destino_si]}")
                asm_instrucciones.append(f"    JMP {etiquetas[destino_no]}")
                continue

        siguiente = next((c.destino for c in conexiones if c.origen == bloque and c.tipo in ["normal", "si", "no"]), None)
        if siguiente:
            asm_instrucciones.append(f"    JMP {etiquetas[siguiente]}")

    asm_instrucciones.append("FIN:")
    asm_instrucciones.append("    MOV AH, 4CH")
    asm_instrucciones.append("    INT 21H")
    asm += "\n".join(asm_instrucciones)
    asm += "\nEND MAIN\n"

    mostrar_codigo_asm(asm)
    return asm


def generar_y_abrir_con_emu8086():
    try:
        if not diagrama:
            raise ValueError("El diagrama está vacío")

        codigo = generar_codigo_asm()
        if not codigo or not isinstance(codigo, str):
            raise ValueError("No se generó código válido")

        # Guardar
        archivo = "programa.asm"
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(codigo)

        os.startfile(archivo)  # EMU8086 lo abrirá

    except Exception as e:
        ventana_error = Toplevel()
        ventana_error.title("Error")
        ventana_error.geometry("300x100")
        tk.Label(ventana_error, text=f"Error:\n{str(e)}", fg="red").pack()


def mostrar_codigo_asm(codigo):
    ventana_asm = Toplevel()
    ventana_asm.title("Código Ensamblador")
    ventana_asm.geometry("600x400")
    texto_asm = scrolledtext.ScrolledText(ventana_asm, font=("Courier", 10), bg="black", fg="lightgreen", insertbackground="white")
    texto_asm.pack(fill="both", expand=True)
    texto_asm.insert(tk.END, codigo)


import re

def traducir_c_a_asm(codigo_c: str) -> str:
    asm = ".MODEL SMALL\n.STACK 100H\n.DATA\n"
    instrucciones = []
    variables = set()
    mensajes = []
    etiquetas = []
    salto_stack = []
    etiqueta_id = 0

    lineas = [line.strip() for line in codigo_c.strip().splitlines() if line.strip()]
    
    # Preprocesar todas las declaraciones
    for linea in lineas:
        # int x = 5;
        match = re.match(r"int\s+(\w+)\s*=\s*(\d+);", linea)
        if match:
            var, val = match.groups()
            variables.add(var)
            instrucciones.append(f"    MOV {var}, {val}")
        # int x;
        match = re.match(r"int\s+(\w+);", linea)
        if match:
            var = match.group(1)
            variables.add(var)

    i = 0
    while i < len(lineas):
        linea = lineas[i]

        if re.match(r"int\s+", linea):
            i += 1
            continue

        # printf("texto");
        match = re.match(r'printf\("([^"]+)"\);', linea)
        if match:
            msg = match.group(1)
            label = f"msg_{len(mensajes)}"
            mensajes.append((label, msg))
            instrucciones.append(f"    LEA DX, {label}")
            instrucciones.append("    MOV AH, 09H")
            instrucciones.append("    INT 21H")
            i += 1
            continue

        # printf("texto", var);
        match = re.match(r'printf\("([^"]+)",\s*(\w+)\);', linea)
        if match:
            msg, var = match.groups()
            label = f"msg_{len(mensajes)}"
            mensajes.append((label, msg))
            instrucciones.append(f"    LEA DX, {label}")
            instrucciones.append("    MOV AH, 09H")
            instrucciones.append("    INT 21H")
            instrucciones.append(f"    MOV AL, {var}")
            instrucciones.append("    ADD AL, 30h")
            instrucciones.append("    MOV DL, AL")
            instrucciones.append("    MOV AH, 02H")
            instrucciones.append("    INT 21H")
            i += 1
            continue

        # x = x + 1;
        match = re.match(r"(\w+)\s*=\s*(\w+)\s*\+\s*(\d+);", linea)
        if match:
            dest, op1, op2 = match.groups()
            instrucciones.append(f"    MOV AL, {op1}")
            instrucciones.append(f"    ADD AL, {op2}")
            instrucciones.append(f"    MOV {dest}, AL")
            i += 1
            continue

        # x = x - 1;
        match = re.match(r"(\w+)\s*=\s*(\w+)\s*-\s*(\d+);", linea)
        if match:
            dest, op1, op2 = match.groups()
            instrucciones.append(f"    MOV AL, {op1}")
            instrucciones.append(f"    SUB AL, {op2}")
            instrucciones.append(f"    MOV {dest}, AL")
            i += 1
            continue

        # x = 5;
        match = re.match(r"(\w+)\s*=\s*(\d+);", linea)
        if match:
            var, val = match.groups()
            instrucciones.append(f"    MOV {var}, {val}")
            i += 1
            continue

        # if (x > 0) {
        match = re.match(r"if\s*\((\w+)\s*(==|!=|<=|>=|<|>)\s*(\d+)\)\s*{?", linea)
        if match:
            var, op, val = match.groups()
            etiqueta_id += 1
            etq_si = f"ETQ_SI_{etiqueta_id}"
            etq_fin = f"ETQ_ENDIF_{etiqueta_id}"
            salto_stack.append(etq_fin)
            operadores = {">": "JG", "<": "JL", ">=": "JGE", "<=": "JLE", "==": "JE", "!=": "JNE"}
            instrucciones.append(f"    MOV AL, {var}")
            instrucciones.append(f"    CMP AL, {val}")
            instrucciones.append(f"    {operadores[op]} {etq_si}")
            instrucciones.append(f"    JMP {etq_fin}")
            instrucciones.append(f"{etq_si}:")
            i += 1
            continue

        # else {
        if re.match(r"else\s*{?", linea):
            etq_fin = salto_stack.pop()
            etiqueta_id += 1
            etq_else = f"ETQ_ELSE_{etiqueta_id}"
            instrucciones.append(f"    JMP {etq_fin}")
            instrucciones.append(f"{etq_else}:")
            salto_stack.append(etq_fin)
            i += 1
            continue

        # while (x > 0) {
        match = re.match(r"while\s*\((\w+)\s*(==|!=|<=|>=|<|>)\s*(\d+)\)\s*{?", linea)
        if match:
            var, op, val = match.groups()
            etiqueta_id += 1
            etq_ini = f"ETQ_WHILE_{etiqueta_id}"
            etq_body = f"ETQ_BODY_{etiqueta_id}"
            etq_fin = f"ETQ_WEND_{etiqueta_id}"
            salto_stack.append((etq_ini, etq_fin))
            operadores = {">": "JG", "<": "JL", ">=": "JGE", "<=": "JLE", "==": "JE", "!=": "JNE"}
            instrucciones.append(f"{etq_ini}:")
            instrucciones.append(f"    MOV AL, {var}")
            instrucciones.append(f"    CMP AL, {val}")
            instrucciones.append(f"    {operadores[op]} {etq_body}")
            instrucciones.append(f"    JMP {etq_fin}")
            instrucciones.append(f"{etq_body}:")
            i += 1
            continue

        # for (i = 0; i < 3; i++) {
        match = re.match(r"for\s*\(\s*(\w+)\s*=\s*(\d+);\s*\1\s*<\s*(\d+);\s*\1\+\+\s*\)\s*{?", linea)
        if match:
            var, ini, fin = match.groups()
            variables.add(var)
            etiqueta_id += 1
            etq_ini = f"ETQ_FOR_{etiqueta_id}"
            etq_body = f"ETQ_FOR_BODY_{etiqueta_id}"
            etq_end = f"ETQ_FOR_END_{etiqueta_id}"
            salto_stack.append((etq_ini, etq_end, var, fin))
            instrucciones.append(f"    MOV {var}, {ini}")
            instrucciones.append(f"{etq_ini}:")
            instrucciones.append(f"    MOV AL, {var}")
            instrucciones.append(f"    CMP AL, {fin}")
            instrucciones.append(f"    JL {etq_body}")
            instrucciones.append(f"    JMP {etq_end}")
            instrucciones.append(f"{etq_body}:")
            i += 1
            continue

        # cierre de bloques: }
        if linea == "}":
            if salto_stack:
                top = salto_stack.pop()
                if isinstance(top, str):  # if/else
                    instrucciones.append(f"{top}:")
                elif len(top) == 2:  # while
                    etq_ini, etq_fin = top
                    instrucciones.append(f"    JMP {etq_ini}")
                    instrucciones.append(f"{etq_fin}:")
                elif len(top) == 4:  # for
                    etq_ini, etq_fin, var, _ = top
                    instrucciones.append(f"    INC {var}")
                    instrucciones.append(f"    JMP {etq_ini}")
                    instrucciones.append(f"{etq_fin}:")
            i += 1
            continue

        i += 1

    for var in variables:
        asm += f"    {var} DB 0\n"

    for label, msg in mensajes:
        asm += f"    {label} DB \"{msg}$\"\n"

    asm += ".CODE\nMAIN:\n"
    asm += "    MOV AX, @DATA\n    MOV DS, AX\n"
    asm += "\n".join(instrucciones)
    asm += "\n    MOV AH, 4CH\n    INT 21H\nEND MAIN\n"
    return asm



def traducir_c_actual_a_asm():
    try:
        codigo_c = generar_codigo_c()
        asm = traducir_c_a_asm(codigo_c)
        mostrar_codigo_asm(asm)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo traducir el código C:\n{e}")


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

import re
from tkinter import messagebox

def validar_diagrama():
    errores = []

    # 1. Verificar que haya al menos un inicio y un fin
    tipos = [b.tipo for b in diagrama]
    if tipos.count("inicio") != 1:
        errores.append("Debe haber exactamente un bloque 'inicio'.")
    if "fin" not in tipos:
        errores.append("Debe haber al menos un bloque 'fin'.")

    # 2. Revisar conexiones por bloque
    for i, bloque in enumerate(diagrama):
        salidas = [c for c in conexiones if c.origen == bloque]
        entradas = [c for c in conexiones if c.destino == bloque]

        if bloque.tipo != "fin" and not salidas:
            errores.append(f"Bloque {i} ({bloque.tipo}): no tiene salida.")
        if bloque.tipo != "inicio" and not entradas:
            errores.append(f"Bloque {i} ({bloque.tipo}): no tiene ninguna conexión de entrada.")

        if bloque.tipo == "decisión":
            tiene_si = any(c.tipo == "si" for c in salidas)
            tiene_no = any(c.tipo == "no" for c in salidas)
            if not tiene_si or not tiene_no:
                errores.append(f"Bloque {i} (decisión): le falta rama {'si' if not tiene_si else 'no'}.")

    # 3. Análisis sintáctico por tipo
    for i, bloque in enumerate(diagrama):
        if not bloque.contenido:
            continue
        texto = bloque.contenido.strip()

        if bloque.tipo == "entrada":
            if not re.match(r"^\w+\s*=\s*\d+$", texto):
                errores.append(f"Bloque {i} (entrada): debe tener formato 'variable = valor'.")

        elif bloque.tipo == "proceso":
            valido = (
                re.match(r"^\w+\s*=\s*\w+(\s*[\+\-\*/]\s*\w+)?$", texto) or
                re.match(r"^\w+\+\+$", texto) or
                re.match(r"^\w+\s*\+=\s*1$", texto) or
                re.match(r'printf\(\s*".*?"\s*(,\s*\w+)?\s*\)', texto)  # permite printf dentro de proceso
            )
            if not valido:
                errores.append(f"Bloque {i} (proceso): expresión inválida '{texto}'.")


        elif bloque.tipo == "decisión":
            if not any(op in texto for op in ["<", ">", "<=", ">=", "==", "!="]):
                errores.append(f"Bloque {i} (decisión): debe contener un operador de comparación.")

        elif bloque.tipo == "salida":
            if "printf" in texto:
                if not re.match(r'printf\(\s*".*?"\s*,\s*\w+\s*\)', texto):
                    errores.append(f"Bloque {i} (salida): printf debe tener formato '\"mensaje\", variable'.")

    # 4. Mostrar errores o éxito
    if errores:
        messagebox.showerror("Errores en el diagrama", "\n".join(errores))
    else:
        messagebox.showinfo("Validación exitosa", "No se encontraron errores en el diagrama.")





def editar_bloque():
    global bloque_seleccionado
    
    if not bloque_seleccionado:
        tk.messagebox.showwarning("Advertencia", "No hay ningún bloque seleccionado")
        return
    
    # Ventana de edición
    ventana_edicion = Toplevel()
    ventana_edicion.title(f"Editar Bloque {bloque_seleccionado.tipo}")
    ventana_edicion.geometry("400x220")
    
    # Contenido actual
    contenido_actual = bloque_seleccionado.contenido if bloque_seleccionado.contenido else ""
    
    # Etiqueta y campo de texto
    tk.Label(ventana_edicion, text="Nuevo contenido:").pack(pady=5)
    texto_edicion = tk.Text(ventana_edicion, height=8, width=40)
    texto_edicion.pack(pady=5)
    texto_edicion.insert(tk.END, contenido_actual)
    
    # Función para guardar cambios
    def guardar_cambios():
        nuevo_contenido = texto_edicion.get("1.0", tk.END).strip()
        bloque_seleccionado.contenido = nuevo_contenido
        dibujar_bloques()
        mostrar_diagrama()
        ventana_edicion.destroy()
        tk.messagebox.showinfo("Éxito", "Bloque actualizado correctamente")
    
    # Botón de guardar
    tk.Button(ventana_edicion, text="Guardar Cambios", command=guardar_cambios, bg="green", fg="white").pack(pady=10)


# --- Interfaz principal ---
ventana = tk.Tk()
ventana.title("Proyecto - Compiladores")
ventana.geometry("1000x650")  # Aumentamos un poco el tamaño
ventana.configure(bg="#2c3e50")  # Fondo oscuro moderno

# --- Frame superior para botones de bloques ---
frame_bloques = tk.Frame(ventana, bg="#34495e", padx=5, pady=5)
frame_bloques.pack(fill=tk.X, padx=5, pady=(5,0))

# Estilo para los botones
btn_style = {
    "bg": "#3498db", 
    "fg": "white", 
    "font": ("Arial", 9, "bold"), 
    "relief": tk.GROOVE, 
    "borderwidth": 2,
    "width": 12,
    "height": 1
}

# Botones de tipos de bloques
tipos = ['inicio', 'entrada', 'proceso', 'decisión', 'salida', 'fin']
for i, tipo in enumerate(tipos):
    b = tk.Button(
        frame_bloques, 
        text=tipo.upper(), 
        command=lambda t=tipo: agregar_bloque(t),
        **btn_style
    )
    b.grid(row=0, column=i, padx=3, pady=2)

# --- Frame para botones de acciones ---
frame_acciones = tk.Frame(ventana, bg="#34495e", padx=5, pady=5)
frame_acciones.pack(fill=tk.X, padx=5, pady=(0,5))

# Botones de acciones principales
acciones_principales = [
    ("Limpiar Todo", limpiar_diagrama, "#e74c3c"),
    ("Guardar", guardar_diagrama, "#2ecc71"),
    ("Cargar", cargar_diagrama, "#3498db"),
    ("Editar Bloque", editar_bloque, "#9b59b6"),
    ("Validar Diagrama", validar_diagrama, "#1abc9c")  # <-- esta línea estaba suelta o mal cerrada

]


for i, (texto, comando, color) in enumerate(acciones_principales):
    btn = tk.Button(
        frame_acciones,
        text=texto,
        command=comando,
        bg=color,
        fg="white",
        font=("Arial", 9, "bold"),
        width=12,
        height=1
    )
    btn.grid(row=0, column=i, padx=3, pady=2)

# Botones de generación de código
acciones_codigo = [
    ("Generar C", on_generar_c_click, "#f1c40f", "black"),
    ("Traducir a ASM", generar_codigo_asm, "#e67e22", "black"),
    ("Abrir EMU8086", generar_y_abrir_con_emu8086, "#e84393", "white")
]

for i, (texto, comando, color, fg) in enumerate(acciones_codigo, start=len(acciones_principales)):
    btn = tk.Button(
        frame_acciones,
        text=texto,
        command=comando,
        bg=color,
        fg=fg,
        font=("Arial", 9, "bold"),
        width=12,
        height=1
    )
    btn.grid(row=0, column=i, padx=3, pady=2)

# --- Frame principal con canvas y texto ---
frame_principal = tk.Frame(ventana, bg="#2c3e50")
frame_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))

# Panel del diagrama (canvas con scroll)
frame_canvas = tk.Frame(frame_principal, bg="#34495e")
frame_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

# Scrollbars para el canvas
scroll_y = tk.Scrollbar(frame_canvas)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

scroll_x = tk.Scrollbar(frame_canvas, orient=tk.HORIZONTAL)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

# Canvas de dibujo
canvas = tk.Canvas(
    frame_canvas,
    width=700,
    height=500,
    bg="white",
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set,
    scrollregion=(0, 0, 2000, 2000),
    highlightthickness=0
)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll_y.config(command=canvas.yview)
scroll_x.config(command=canvas.xview)

# Panel de texto (previsualización del diagrama)
frame_texto = tk.Frame(frame_principal, bg="#34495e")
frame_texto.pack(side=tk.RIGHT, fill=tk.BOTH)

label_texto = tk.Label(
    frame_texto, 
    text="Vista Previa del Diagrama", 
    bg="#34495e", 
    fg="white", 
    font=("Arial", 10, "bold")
)
label_texto.pack(fill=tk.X)

texto = tk.Text(
    frame_texto,
    width=35,
    height=30,
    bg="#1e272e",
    fg="#f5f6fa",
    font=("Consolas", 9),
    insertbackground="white",
    wrap=tk.WORD,
    padx=10,
    pady=10
)
texto.pack(fill=tk.BOTH, expand=True)

# Barra de scroll para el texto
scroll_text = tk.Scrollbar(frame_texto)
scroll_text.pack(side=tk.RIGHT, fill=tk.Y)
texto.config(yscrollcommand=scroll_text.set)
scroll_text.config(command=texto.yview)

# --- Configuración de eventos ---
canvas.bind("<Button-1>", on_canvas_click)
canvas.bind("<B1-Motion>", on_canvas_drag)
canvas.bind("<ButtonRelease-1>", on_canvas_release)
canvas.bind("<Double-Button-1>", lambda e: editar_bloque())
canvas.tag_bind("puerto", "<Button-1>", on_puerto_click)
canvas.tag_bind("puerto", "<B1-Motion>", on_puerto_drag)
canvas.tag_bind("puerto", "<ButtonRelease-1>", on_puerto_release)


# --- Función de Zoom ---
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

# Zoom con Ctrl + Rueda del mouse
scale = 1.0  # Variable global para controlar el zoom
canvas.bind("<MouseWheel>", zoom)
canvas.bind("<Button-4>", zoom)
canvas.bind("<Button-5>", zoom)

# --- Barra de estado ---
barra_estado = tk.Label(
    ventana,
    text="Proyecto Compiladores 2025 | Diagrama de Flujo v1.0",
    bd=1,
    relief=tk.SUNKEN,
    anchor=tk.W,
    bg="#2c3e50",
    fg="#ecf0f1",
    font=("Arial", 8)
)
barra_estado.pack(fill=tk.X, padx=5, pady=(0,5))

ventana.mainloop()
