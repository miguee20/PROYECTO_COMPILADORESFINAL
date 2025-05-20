import tkinter as tk
from tkinter import simpledialog, filedialog, scrolledtext
import json

# ------------------------
# BLOQUES LÓGICOS
# ------------------------
class Bloque:
    def __init__(self, tipo, contenido=None):
        self.tipo = tipo
        self.contenido = contenido
        self.si = []
        self.no = []

# ------------------------
# CONEXIONES VISUALES
# ------------------------
class Connection:
    def __init__(self, canvas, shape1, shape2):
        self.canvas = canvas
        self.shape1 = shape1
        self.shape2 = shape2
        self.line = self.canvas.create_line(shape1.x, shape1.y, shape2.x, shape2.y, arrow=tk.LAST, width=3, fill="#1565C0")
        shape1.connections.append(self)
        shape2.connections.append(self)

    def update_position(self):
        self.canvas.coords(self.line, self.shape1.x, self.shape1.y, self.shape2.x, self.shape2.y)

    def delete(self):
        self.canvas.delete(self.line)

# ------------------------
# FORMAS VISUALES
# ------------------------
class Shape:
    PORT_SIZE = 8

    def __init__(self, app, canvas, shape_type, x, y):
        self.app = app
        self.canvas = canvas
        self.shape_type = shape_type
        self.x, self.y = x, y
        self.text = self.default_text()
        self.connections = []
        self.drag_data = {"x": 0, "y": 0}
        self.item = self.draw_shape()
        self.text_id = self.canvas.create_text(x, y, text=self.text, font=("Arial", 14, "bold"), fill="#0D47A1")
        self.ports = {}
        self.create_ports()
        self.hide_ports()
        self.bind_events()

    def default_text(self):
        return {"oval": "Inicio/Fin", "rectangle": "Proceso", "diamond": "Decisión"}.get(self.shape_type, "")

    def draw_shape(self):
        if self.shape_type == "oval":
            return self.canvas.create_oval(self.x-50, self.y-30, self.x+50, self.y+30, fill="#BBDEFB", outline="#0D47A1", width=2)
        elif self.shape_type == "rectangle":
            return self.canvas.create_rectangle(self.x-60, self.y-30, self.x+60, self.y+30, fill="#64B5F6", outline="#0D47A1", width=2)
        elif self.shape_type == "diamond":
            return self.canvas.create_polygon(self.x, self.y-40, self.x+60, self.y, self.x, self.y+40, self.x-60, self.y, fill="#90CAF9", outline="#0D47A1", width=2)

    def create_ports(self):
        s = self.PORT_SIZE
        if self.shape_type in ["oval", "rectangle"]:
            offsets = {
                "top":    (self.x, self.y - 30 - s//2),
                "bottom": (self.x, self.y + 30 - s//2),
                "left":   (self.x - 60 - s//2 if self.shape_type=="rectangle" else self.x - 50 - s//2, self.y),
                "right":  (self.x + 60 - s//2 if self.shape_type=="rectangle" else self.x + 50 - s//2, self.y)
            }
        elif self.shape_type == "diamond":
            offsets = {
                "top":    (self.x - s//2, self.y - 40 - s//2),
                "bottom": (self.x - s//2, self.y + 40 - s//2),
                "left":   (self.x - 60 - s//2, self.y - s//2),
                "right":  (self.x + 60 - s//2, self.y - s//2)
            }
        else:
            offsets = {}

        for pos, (cx, cy) in offsets.items():
            port = self.canvas.create_oval(cx, cy, cx+s, cy+s, fill="black", state='hidden', tags=("port",))
            self.ports[pos] = port
            self.canvas.tag_bind(port, "<Button-1>", lambda e, p=pos: self.app.start_connection(self, p, e))

    def show_ports(self):
        for port in self.ports.values():
            self.canvas.itemconfigure(port, state='normal')

    def hide_ports(self):
        for port in self.ports.values():
            self.canvas.itemconfigure(port, state='hidden')

    def move_ports(self, dx, dy):
        for port in self.ports.values():
            self.canvas.move(port, dx, dy)

    def bind_events(self):
        for item in [self.item, self.text_id]:
            self.canvas.tag_bind(item, "<Button-1>", self.on_click)
            self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(item, "<Double-1>", self.edit_text)

    def on_click(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.app.handle_selection(self)

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.item, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        self.move_ports(dx, dy)
        self.x += dx
        self.y += dy
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        for conn in self.connections:
            conn.update_position()

    def edit_text(self, event):
        new_text = simpledialog.askstring("Editar texto", "Nuevo texto:", initialvalue=self.text)
        if new_text is not None:
            self.text = new_text
            self.canvas.itemconfig(self.text_id, text=self.text)

    def delete(self):
        self.canvas.delete(self.item)
        self.canvas.delete(self.text_id)
        for port in self.ports.values():
            self.canvas.delete(port)
        for conn in self.connections[:]:
            conn.delete()

# ------------------------
# APP PRINCIPAL
# ------------------------
class FlowchartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Diagramas de Flujo")
        self.root.configure(bg="#F0F8FF")
        self.shapes = []
        self.connections = []
        self.selected_shape = None

        self.toolbar = tk.Frame(root, bg="midnight blue")
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas = tk.Canvas(root, bg="white", width=1000, height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.add_buttons()

        self.temp_line = None
        self.connection_start = None
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def add_buttons(self):
        style = {"bg": "#81D4FA", "fg": "white", "font": ("Arial", 12, "bold"), "relief": "raised", "bd": 3, "width": 12, "height": 2}

        tk.Button(self.toolbar, text="Inicio/Fin", command=lambda: self.add_shape("oval"), **style).pack(side=tk.LEFT, padx=3, pady=5)
        tk.Button(self.toolbar, text="Proceso", command=lambda: self.add_shape("rectangle"), **style).pack(side=tk.LEFT, padx=3, pady=5)
        tk.Button(self.toolbar, text="Decisión", command=lambda: self.add_shape("diamond"), **style).pack(side=tk.LEFT, padx=3, pady=5)
        tk.Button(self.toolbar, text="Código C", command=self.generar_codigo_c, bg="gold", fg="black", font=("Arial", 12, "bold"), width=12, height=2).pack(side=tk.LEFT, padx=3)
        tk.Button(self.toolbar, text="ASM", command=self.generar_codigo_asm, bg="orange", fg="black", font=("Arial", 12, "bold"), width=12, height=2).pack(side=tk.LEFT, padx=3)
        tk.Button(self.toolbar, text="Guardar", command=self.guardar_diagrama, bg="#0288D1", fg="white", font=("Arial", 12, "bold"), width=12, height=2).pack(side=tk.RIGHT, padx=3)
        tk.Button(self.toolbar, text="Cargar", command=self.cargar_diagrama, bg="#0288D1", fg="white", font=("Arial", 12, "bold"), width=12, height=2).pack(side=tk.RIGHT, padx=3)



    def add_shape(self, shape_type):
        x, y = 200 + len(self.shapes)*30, 150 + len(self.shapes)*30
        shape = Shape(self, self.canvas, shape_type, x, y)
        self.shapes.append(shape)

    def handle_selection(self, shape):
        if self.selected_shape and self.selected_shape != shape:
            self.selected_shape.hide_ports()
        self.selected_shape = shape
        self.selected_shape.show_ports()

    def connect_shapes(self, shape1, shape2):
        if shape1 == shape2:
            return
        for conn in self.connections:
            if (conn.shape1 == shape1 and conn.shape2 == shape2) or (conn.shape1 == shape2 and conn.shape2 == shape1):
                return
        conn = Connection(self.canvas, shape1, shape2)
        self.connections.append(conn)

    def clear_diagram(self):
        for shape in self.shapes:
            shape.delete()
        self.shapes.clear()
        self.connections.clear()
        self.canvas.delete("all")

    def start_connection(self, shape, port, event):
        self.connection_start = (shape, port)
        x, y = event.x, event.y
        self.temp_line = self.canvas.create_line(shape.x, shape.y, x, y, arrow=tk.LAST, dash=(4, 2), fill="gray", width=2)
        self.canvas.bind("<Motion>", self.update_temp_line)

    def update_temp_line(self, event):
        if self.temp_line and self.connection_start:
            start_shape, start_port = self.connection_start
            px, py = self.get_port_center(start_shape, start_port)
            self.canvas.coords(self.temp_line, px, py, event.x, event.y)

    def on_mouse_release(self, event):
        if self.temp_line and self.connection_start:
            self.canvas.unbind("<Motion>")
            self.canvas.delete(self.temp_line)
            self.temp_line = None

            target_shape = self.find_shape_at(event.x, event.y)
            start_shape, _ = self.connection_start
            if target_shape and target_shape != start_shape:
                self.connect_shapes(start_shape, target_shape)

            self.connection_start = None

    def get_port_center(self, shape, port_name):
        s = shape.PORT_SIZE
        coords = self.canvas.coords(shape.ports[port_name])
        cx = (coords[0] + coords[2]) / 2
        cy = (coords[1] + coords[3]) / 2
        return cx, cy

    def find_shape_at(self, x, y):
        for shape in self.shapes:
            bbox = self.canvas.bbox(shape.item)
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                return shape
        return None

    def export_logic(self):
        logic_blocks = []
        id_map = {}
        for shape in self.shapes:
            tipo = {"oval": "inicio" if "inicio" in shape.text.lower() else "fin", "rectangle": "proceso", "diamond": "decisión"}.get(shape.shape_type, "proceso")
            bloque = Bloque(tipo, shape.text)
            logic_blocks.append(bloque)
            id_map[id(shape)] = bloque
        for conn in self.connections:
            b1 = id_map[id(conn.shape1)]
            b2 = id_map[id(conn.shape2)]
            if b1.tipo == "decisión":
                if not b1.si:
                    b1.si.append(b2)
                else:
                    b1.no.append(b2)
            else:
                b1.si.append(b2)
        return logic_blocks

    def generar_codigo_c(self):
        bloques = self.export_logic()
        codigo = "#include <stdio.h>\n\nint main() {\n"
        indent = "    "
        for bloque in bloques:
            if bloque.tipo == "entrada":
                codigo += f"{indent}int {bloque.contenido};\n"
                codigo += f"{indent}scanf(\"%d\", &{bloque.contenido});\n"
            elif bloque.tipo == "proceso":
                codigo += f"{indent}{bloque.contenido};\n"
            elif bloque.tipo == "salida":
                codigo += f"{indent}printf(\"%d\\n\", {bloque.contenido});\n"
            elif bloque.tipo == "decisión":
                codigo += f"{indent}if ({bloque.contenido}) {{\n"
                for si in bloque.si:
                    codigo += f"{indent*2}{si.contenido};\n"
                codigo += f"{indent}}} else {{\n"
                for no in bloque.no:
                    codigo += f"{indent*2}{no.contenido};\n"
                codigo += f"{indent}}}\n"
            elif bloque.tipo == "fin":
                codigo += f"{indent}return 0;\n"
        codigo += "}\n"
        self.mostrar_codigo("Código en C", codigo)

    def generar_codigo_asm(self):
        self.mostrar_codigo("ASM", "; ASM generado (completar lógica si es necesario)")

    def mostrar_codigo(self, titulo, codigo):
        ventana = tk.Toplevel()
        ventana.title(titulo)
        text = scrolledtext.ScrolledText(ventana, font=("Courier", 10), bg="black", fg="lime" if "C" in titulo else "lightgreen")
        text.pack(fill="both", expand=True)
        text.insert("1.0", codigo)

    def guardar_diagrama(self):
        data = [{"type": s.shape_type, "text": s.text, "x": s.x, "y": s.y} for s in self.shapes]
        conns = [(self.shapes.index(c.shape1), self.shapes.index(c.shape2)) for c in self.connections]
        ruta = filedialog.asksaveasfilename(defaultextension=".json")
        if ruta:
            with open(ruta, "w") as f:
                json.dump({"shapes": data, "connections": conns}, f)

    def cargar_diagrama(self):
        ruta = filedialog.askopenfilename(filetypes=[("Diagramas", "*.json")])
        if ruta:
            with open(ruta) as f:
                contenido = json.load(f)
            self.clear_diagram()
            for sdata in contenido["shapes"]:
                shape = Shape(self, self.canvas, sdata["type"], sdata["x"], sdata["y"])
                shape.text = sdata["text"]
                self.canvas.itemconfig(shape.text_id, text=shape.text)
                self.shapes.append(shape)
            for i1, i2 in contenido["connections"]:
                self.connect_shapes(self.shapes[i1], self.shapes[i2])

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowchartApp(root)
    root.mainloop()