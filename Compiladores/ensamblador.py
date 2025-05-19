class GeneradorEnsamblador:
    def __init__(self):
        self.codigo = []
        self.variables = {}
        self.etiqueta_contador = 0

    def generar(self, nodo):
        metodo = f'visitar_{type(nodo).__name__}'
        if hasattr(self, metodo):
            return getattr(self, metodo)(nodo)
        else:
            raise Exception(f'No se ha implementado la generación para {type(nodo).__name__}')

    def generar_etiqueta(self):
        etiqueta = f'etiqueta_{self.etiqueta_contador}'
        self.etiqueta_contador += 1
        return etiqueta

    def visitar_NodoPrograma(self, nodo):
        # Declaración de variables al principio
        self.codigo.append("section .data")
        for var in self.variables:
            self.codigo.append(f"{var} dq 0")  # dq: define quadword (64 bits)

        self.codigo.append("section .text")
        self.codigo.append("global _start")
        self.codigo.append("_start:")

        for funcion in nodo.funciones:
            self.generar(funcion)

        # syscall exit (Linux, 64-bit)
        self.codigo.append("mov rax, 60")  # syscall: exit
        self.codigo.append("mov rdi, 0")   # exit code 0
        self.codigo.append("syscall")

    def visitar_NodoFuncion(self, nodo):
        self.codigo.append(f"{nodo.nombre}:")
        self.codigo.append("push rbp")
        self.codigo.append("mov rbp, rsp")

        for var in nodo.parametros:
            self.variables[var.nombre] = 0

        for instruccion in nodo.cuerpo:
            self.generar(instruccion)

        self.codigo.append("mov rsp, rbp")
        self.codigo.append("pop rbp")
        self.codigo.append("ret")

    def visitar_NodoAsignacion(self, nodo):
        valor = self.generar(nodo.expresion)
        self.codigo.append(f"mov rax, {valor}")
        self.codigo.append(f"mov [{nodo.nombre}], rax")

    def visitar_NodoNumero(self, nodo):
        return str(nodo.valor)

    def visitar_NodoOperacion(self, nodo):
        izq = self.generar(nodo.izquierda)
        der = self.generar(nodo.derecha)
        self.codigo.append(f"mov rax, {izq}")
        if nodo.operador == '+':
            self.codigo.append(f"add rax, {der}")
        elif nodo.operador == '-':
            self.codigo.append(f"sub rax, {der}")
        elif nodo.operador == '*':
            self.codigo.append(f"imul rax, {der}")
        elif nodo.operador == '/':
            self.codigo.append("mov rdx, 0")  # limpiar rdx antes de div
            self.codigo.append(f"mov rbx, {der}")
            self.codigo.append("div rbx")  # resultado en rax
        return "rax"

    def visitar_NodoRetorno(self, nodo):
        valor = self.generar(nodo.expresion)
        self.codigo.append(f"mov rax, {valor}")
        self.codigo.append("mov rsp, rbp")
        self.codigo.append("pop rbp")
        self.codigo.append("ret")

    def visitar_NodoDeclaracion(self, nodo):
        self.variables[nodo.nombre] = 0
        if nodo.expresion:
            valor = self.generar(nodo.expresion)
            self.codigo.append(f"mov rax, {valor}")
            self.codigo.append(f"mov [{nodo.nombre}], rax")

    def visitar_NodoIdentificador(self, nodo):
        return f"[{nodo.nombre}]"

    def visitar_NodoLlamadaFuncion(self, nodo):
        for arg in reversed(nodo.argumentos):
            valor = self.generar(arg)
            self.codigo.append(f"push {valor}")

        self.codigo.append(f"call {nodo.nombre}")
        self.codigo.append(f"add rsp, {8 * len(nodo.argumentos)}")  # cada argumento ocupa 8 bytes
        return "rax"

    def visitar_NodoPrint(self, nodo):
        valor = self.generar(nodo.expresion)
        self.codigo.append(f"; Print no implementado. Valor: {valor}")
        # Se puede implementar con syscall write si deseas (puedo ayudarte con eso)
    
    def recolectar_variables(self, nodo):
        if hasattr(nodo, 'cuerpo'):
            for instr in nodo.cuerpo:
                self.recolectar_variables(instr)
        elif hasattr(nodo, 'expresion'):
            self.recolectar_variables(nodo.expresion)
        elif hasattr(nodo, 'izquierda') and hasattr(nodo, 'derecha'):
            self.recolectar_variables(nodo.izquierda)
            self.recolectar_variables(nodo.derecha)
        elif hasattr(nodo, 'argumentos'):
            for arg in nodo.argumentos:
                self.recolectar_variables(arg)
        elif type(nodo).__name__ == "NodoDeclaracion":
            self.variables[nodo.nombre] = 0
            if nodo.expresion:
                self.recolectar_variables(nodo.expresion)

    def generar_codigo(self, ast):
        self.codigo = []
        self.variables = {}
        self.recolectar_variables(ast)
        self.generar(ast)
        return "\n".join(self.codigo)



def ensamblador_a_lenguaje_maquina(ensamblador):
    opcodes = {
        'mov': 'B8',
        'add': '03',
        'sub': '2B',
        'imul': 'F7',
        'idiv': 'F7',
        'cwd': '99',
        'push': '50',
        'pop': '58',
        'call': 'E8',
        'ret': 'C3',
        'int 21h': 'CD 21',
        'hlt': 'F4',
    }

    instrucciones = ensamblador.split('\n')
    lenguaje_maquina = []

    for instr in instrucciones:
        instr = instr.strip().lower()
        for key in opcodes:
            if instr.startswith(key):
                lenguaje_maquina.append(opcodes[key])
                break

    return ' '.join(lenguaje_maquina)


def generar_codigo_lenguaje_maquina(codigo_ensamblador):
    return ensamblador_a_lenguaje_maquina(codigo_ensamblador)