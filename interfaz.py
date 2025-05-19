import tkinter as tk
from tkinter import simpledialog

class Connection:
    def __init__(self, canvas, shape1, shape2):
        self.canvas = canvas
        self.shape1 = shape1
        self.shape2 = shape2
        self.line = self.canvas.create_line(
            shape1.x, shape1.y, shape2.x, shape2.y,
            arrow=tk.LAST, width=2
        )
        # Añadimos esta conexión a ambas figuras
        shape1.connections.append(self)
        shape2.connections.append(self)

    def update_position(self):
        self.canvas.coords(self.line, self.shape1.x, self.shape1.y, self.shape2.x, self.shape2.y)

    def delete(self):
        self.canvas.delete(self.line)

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
        self.text_id = self.canvas.create_text(x, y, text=self.text)
        # Crear puertos (cuatro círculos en los 4 lados)
        self.ports = {}
        self.create_ports()
        self.hide_ports()  # Al inicio ocultos
        self.bind_events()

    def default_text(self):
        return {
            "oval": "Inicio/Fin",
            "rectangle": "Proceso",
            "diamond": "Decisión"
        }.get(self.shape_type, "")

    def draw_shape(self):
        if self.shape_type == "oval":
            return self.canvas.create_oval(self.x-50, self.y-30, self.x+50, self.y+30, fill="lightblue", outline="black")
        elif self.shape_type == "rectangle":
            return self.canvas.create_rectangle(self.x-60, self.y-30, self.x+60, self.y+30, fill="lightgreen", outline="black")
        elif self.shape_type == "diamond":
            return self.canvas.create_polygon(self.x, self.y-40, self.x+60, self.y, self.x, self.y+40, self.x-60, self.y,
                                              fill="#FFD966", outline="black")

    def create_ports(self):
        s = self.PORT_SIZE
        # posiciones relativas según la figura:
        # arriba, abajo, izquierda, derecha
        # Para figuras rectangulares y ovales:
        # Ajustamos según el tipo para que los puertos queden justo al borde
        if self.shape_type == "oval" or self.shape_type == "rectangle":
            offsets = {
                "top":    (self.x, self.y - 30 - s//2),
                "bottom": (self.x, self.y + 30 - s//2),
                "left":   (self.x - 60 - s//2 if self.shape_type=="rectangle" else self.x - 50 - s//2, self.y),
                "right":  (self.x + 60 - s//2 if self.shape_type=="rectangle" else self.x + 50 - s//2, self.y)
            }
        elif self.shape_type == "diamond":
            # Para diamante los puertos se ubican en vértices
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
            # Bindings para puerto
            self.canvas.tag_bind(port, "<Button-1>", lambda e, p=pos: self.app.start_connection(self, p, e))
            # Nota: no movemos puertos individualmente, se mueven con la figura

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
        # Actualizar todas las líneas conectadas
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

class FlowchartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Diagramas de Flujo")
        self.shapes = []
        self.connections = []
        self.selected_shape = None

        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(root, bg="white", width=1000, height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.add_buttons()

        # Variables para la conexión arrastrada
        self.temp_line = None
        self.connection_start = None  # (shape, port)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def add_buttons(self):
        tk.Button(self.toolbar, text="Inicio/Fin", command=lambda: self.add_shape("oval")).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Proceso", command=lambda: self.add_shape("rectangle")).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Decisión", command=lambda: self.add_shape("diamond")).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Borrar Diagrama", fg="red", command=self.clear_diagram).pack(side=tk.RIGHT)
        tk.Label(self.toolbar, text="Haz clic en 2 formas para conectar", fg="gray").pack(side=tk.LEFT)

    def add_shape(self, shape_type):
        x, y = 200 + len(self.shapes)*30, 150 + len(self.shapes)*30
        shape = Shape(self, self.canvas, shape_type, x, y)
        self.shapes.append(shape)

    def handle_selection(self, shape):
        # Deseleccionar el anterior
        if self.selected_shape and self.selected_shape != shape:
            self.selected_shape.hide_ports()
        # Seleccionar el nuevo
        self.selected_shape = shape
        self.selected_shape.show_ports()

    def connect_shapes(self, shape1, shape2):
        # Evitar conectar la misma figura o conexión repetida
        if shape1 == shape2:
            return
        # Checar si ya existe conexión entre estas dos
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

    # Método llamado desde los puertos al hacer click en uno
    def start_connection(self, shape, port, event):
        # Guardamos el inicio
        self.connection_start = (shape, port)
        x, y = event.x, event.y
        # Creamos línea temporal que sigue el mouse
        self.temp_line = self.canvas.create_line(shape.x, shape.y, x, y, arrow=tk.LAST, dash=(4, 2), fill="gray", width=2)
        # Vinculamos movimiento del mouse para actualizar línea
        self.canvas.bind("<Motion>", self.update_temp_line)

    def update_temp_line(self, event):
        if self.temp_line and self.connection_start:
            start_shape, start_port = self.connection_start
            # Coordenadas de inicio puerto
            px, py = self.get_port_center(start_shape, start_port)
            self.canvas.coords(self.temp_line, px, py, event.x, event.y)

    def on_mouse_release(self, event):
        if self.temp_line and self.connection_start:
            # Quitar seguimiento de mouse
            self.canvas.unbind("<Motion>")
            self.canvas.delete(self.temp_line)
            self.temp_line = None

            # Detectar si se suelta sobre otro shape
            target_shape = self.find_shape_at(event.x, event.y)
            start_shape, _ = self.connection_start
            if target_shape and target_shape != start_shape:
                self.connect_shapes(start_shape, target_shape)

            self.connection_start = None

    def get_port_center(self, shape, port_name):
        # Devuelve centro del puerto según su nombre
        s = shape.PORT_SIZE
        coords = self.canvas.coords(shape.ports[port_name])  # [x1,y1,x2,y2]
        cx = (coords[0] + coords[2]) / 2
        cy = (coords[1] + coords[3]) / 2
        return cx, cy

    def find_shape_at(self, x, y):
        # Busca un shape que contenga el punto (x,y)
        for shape in self.shapes:
            # Usamos bbox del shape
            bbox = self.canvas.bbox(shape.item)  # (x1, y1, x2, y2)
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                return shape
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowchartApp(root)
    root.mainloop()
