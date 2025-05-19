import tkinter as tk
from tkinter import simpledialog

class Bloque:
    def __init__(self, canvas, tipo, x, y):
        self.canvas = canvas
        self.tipo = tipo
        self.x = x
        self.y = y
        self.id = None
        self.text_id = None
        self.texto = tipo
        self.crear_bloque()
        self.drag_data = {"x": 0, "y": 0}

        # Eventos para mover
        self.canvas.tag_bind(self.id, "<ButtonPress-1>", self.iniciar_arrastre)
        self.canvas.tag_bind(self.id, "<B1-Motion>", self.arrastrar)
        self.canvas.tag_bind(self.text_id, "<ButtonPress-1>", self.iniciar_arrastre)
        self.canvas.tag_bind(self.text_id, "<B1-Motion>", self.arrastrar)

        # Evento para editar texto
        self.canvas.tag_bind(self.id, "<Double-1>", self.editar_texto)
        self.canvas.tag_bind(self.text_id, "<Double-1>", self.editar_texto)

    def crear_bloque(self):
        w, h = 120, 60
        if self.tipo == "Inicio" or self.tipo == "Fin":
            self.id = self.canvas.create_oval(self.x, self.y, self.x + w, self.y + h, fill="#b3ffb3")
        elif self.tipo == "Entrada/Salida":
            self.id = self.canvas.create_polygon(self.x, self.y+10, self.x+20, self.y, self.x+100, self.y,
                                                 self.x+120, self.y+10, self.x+100, self.y+60,
                                                 self.x+20, self.y+60, fill="#ffffb3", outline="black")
        elif self.tipo == "Proceso":
            self.id = self.canvas.create_rectangle(self.x, self.y, self.x + w, self.y + h, fill="#cce0ff")
        elif self.tipo == "Decisión":
            self.id = self.canvas.create_polygon(self.x+60, self.y, self.x+120, self.y+30, self.x+60,
                                                 self.y+60, self.x, self.y+30, fill="#ffd480", outline="black")
        else:
            self.id = self.canvas.create_rectangle(self.x, self.y, self.x + w, self.y + h, fill="gray")

        self.text_id = self.canvas.create_text(self.x + 60, self.y + 30, text=self.texto, font=("Arial", 10))

    def iniciar_arrastre(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def arrastrar(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def editar_texto(self, event):
        nuevo_texto = simpledialog.askstring("Editar bloque", "Escribe el contenido del bloque:", initialvalue=self.texto)
        if nuevo_texto:
            self.texto = nuevo_texto
            self.canvas.itemconfig(self.text_id, text=self.texto)

    def obtener_centro(self):
        bbox = self.canvas.bbox(self.id)
        x_centro = (bbox[0] + bbox[2]) / 2
        y_centro = (bbox[1] + bbox[3]) / 2
        return x_centro, y_centro

class DiagramaFlujoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Diagramas de Flujo")
        self.geometry("1200x700")
        self.bloques = []
        self.lineas = []
        self.bloque_seleccionado = None
        self._crear_paneles()

    def _crear_paneles(self):
        panel_izquierdo = tk.Frame(self, width=200, bg="#f0f0f0")
        panel_izquierdo.pack(side="left", fill="y")

        titulo = tk.Label(panel_izquierdo, text="Bloques disponibles", bg="#f0f0f0", font=("Arial", 14))
        titulo.pack(pady=10)

        bloques = ["Inicio", "Entrada/Salida", "Proceso", "Decisión", "Fin"]
        for bloque in bloques:
            btn = tk.Button(panel_izquierdo, text=bloque, width=20, height=2,
                            command=lambda b=bloque: self._agregar_bloque(b))
            btn.pack(pady=5)

        generar_btn = tk.Button(panel_izquierdo, text="Generar código C", bg="#c6f5c6", command=self.generar_codigo_c)
        generar_btn.pack(pady=20)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.seleccionar_para_conectar)

    def _agregar_bloque(self, tipo):
        bloque = Bloque(self.canvas, tipo, 100, 100)
        self.bloques.append(bloque)

    def seleccionar_para_conectar(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        for bloque in self.bloques:
            if item == bloque.id or item == bloque.text_id:
                if self.bloque_seleccionado is None:
                    self.bloque_seleccionado = bloque
                else:
                    self._dibujar_conexion(self.bloque_seleccionado, bloque)
                    self.bloque_seleccionado = None
                break

    def _dibujar_conexion(self, bloque1, bloque2):
        x1, y1 = bloque1.obtener_centro()
        x2, y2 = bloque2.obtener_centro()
        linea = self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=2)
        self.lineas.append(linea)

    def generar_codigo_c(self):
        codigo = "// Código generado desde el diagrama de flujo\n"
        for bloque in self.bloques:
            if bloque.tipo == "Inicio":
                codigo += "int main() {\n"
            elif bloque.tipo == "Entrada/Salida":
                codigo += f'    // Entrada/Salida: {bloque.texto}\n'
            elif bloque.tipo == "Proceso":
                codigo += f'    {bloque.texto}\n'
            elif bloque.tipo == "Decisión":
                codigo += f'    if ({bloque.texto}) {{\n        // código\n    }}\n'
            elif bloque.tipo == "Fin":
                codigo += "    return 0;\n}\n"

        print("\n--- CÓDIGO GENERADO ---\n" + codigo)

if __name__ == "__main__":
    app = DiagramaFlujoApp()
    app.mainloop()
