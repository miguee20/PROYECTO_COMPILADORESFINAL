import re

# Op relacional = <, >, =, !, <=, >=, ==, !=,
# Op lógicos = &, &&, |, ||, !
# Definir patrones de tokens

token_patron = {
    "KEYWORD": r'\b(if|else|while|for|return|int|float|void|class|def|print)\b',
    "IDENTIFIER": r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "NUMBER": r'\b\d+\b',
    "OPERATOR": r'<=|>=|==|!=|&&|"|[\+\-\*/=<>\!\||\|\']',
    "DELIMITER": r'[(),;{}]',  # Paréntesis, llaves, punto y coma
    "WHITESPACE": r'\s+'  # Espacios en blanco
}


def tokenize(text):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)

    tokens_encontrados = []

    for match in patron_regex.finditer(text):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":
                tokens_encontrados.append((token, valor))
    return tokens_encontrados


class NodoAST:
    # Clase base para todos los nodos del AST
    def traducir(self):
        raise NotImplementedError("Método traducir no implementado en este nodo")
    
    def generar_codigo(self):
        raise NotImplementedError("Método generar_codigo no implementado en este nodo")


class NodoPrograma(NodoAST):
    def __init__(self, funciones):
        self.funciones = funciones
        self.variables = set()  # Conjunto para almacenar variables

    def recolectar_variables(self, nodo):
        # Recorre el AST y extrae los nombres de las variables.
        if isinstance(nodo, NodoAsignacion):
            self.variables.add(nodo.nombre[1])  # Guardar la variable
        elif isinstance(nodo, NodoIdentificador):
            self.variables.add(nodo.nombre[1])
        elif isinstance(nodo, NodoFuncion):
            for instruccion in nodo.cuerpo:
                self.recolectar_variables(instruccion)
        elif isinstance(nodo, NodoOperacion):
            self.recolectar_variables(nodo.izquierda)
            self.recolectar_variables(nodo.derecha)
        elif isinstance(nodo, NodoIf) or isinstance(nodo, NodoWhile) or isinstance(nodo, NodoFor):
            self.recolectar_variables(nodo.condicion)
            for instruccion in nodo.cuerpo:
                self.recolectar_variables(instruccion)
            if hasattr(nodo, 'sino') and nodo.sino:
                for instruccion in nodo.sino:
                    self.recolectar_variables(instruccion)

    def generar_codigo(self):
        # Genera el código ensamblador incluyendo las variables en .data automáticamente
        self.variables = set()  # Resetear variables
        for funcion in self.funciones:
            self.recolectar_variables(funcion)

        codigo = []

        # Sección de datos (incluye variables detectadas)
        codigo.append("section .data")
        for var in self.variables:
            codigo.append(f"   {var} dd 0")  # entero de 32 bits
        # Agregar variable salto de línea
        codigo.append("   newline db 0xA")  # Salto de línea
        codigo.append("section .bss")
        codigo.append("   char resb 16") # Reservar espacio para un carácter

        # Sección de código
        codigo.append("section .text")
        codigo.append("   global _start")
        
        for funcion in self.funciones:
            if funcion.nombre[1] == 'main':
                # Convertimos main en _start
                codigo.append("_start:")
                for instruccion in funcion.cuerpo:
                    codigo.append(instruccion.generar_codigo())
                codigo.append("   mov eax, 1")  # sys_exit
                codigo.append("   xor ebx, ebx")
                codigo.append("   int 0x80")
            else:
                codigo.append(funcion.generar_codigo())    
        # Función para imprimir un numero
        codigo.append("imprimir:")
        codigo.extend([
                # Convertir número a string (maneja múltiples dígitos)
                "   mov ecx, 10",         # Divisor para conversión
                "   mov edi, char+11",
                "   mov byte [edi], 0",   # Null terminator
                "   dec edi",
                "   mov byte [edi], 0xA", # Newline
                "   dec edi",
                "   mov esi, 2",          # Contador de caracteres (newline + null)",
                
                "convert_loop:",
                "   xor edx, edx",       # Limpiar edx para división
                "   div ecx",             # eax = eax/10, edx = resto
                "   add dl, '0'",         # Convertir a ASCII
                "   mov [edi], dl",       # Almacenar dígito
                "   dec edi",
                "   inc esi",
                "   test eax, eax",       # Verificar si eax es cero
                "   jnz convert_loop",
                
                # Ajustar puntero al inicio del número
                "   inc edi",
                
                # Imprimir el número con newline
                "   mov eax, 4",          # sys_write
                "   mov ebx, 1",          # stdout
                "   mov ecx, edi",        # Puntero al string
                "   mov edx, esi",        # Longitud (dígitos + newline)
                "   int 0x80",
                "   ret"  # Retornar de la función imprimir
            ])
       

        return "\n".join(codigo)
    
    def traducir(self):
        return "\n\n".join(f.traducir() for f in self.funciones)


class NodoFuncion(NodoAST):
    # Nodo que representa una función
    def __init__(self, nombre, tipo_retorno, parametros, cuerpo):
        self.nombre = nombre
        self.tipo_retorno = tipo_retorno
        self.parametros = parametros
        self.cuerpo = cuerpo


    def traducir(self):
        params = ", ".join(p.traducir() for p in self.parametros)
        cuerpo = "\n   ".join(c.traducir() for c in self.cuerpo)
        return f"def {self.nombre[1]}({params}):\n   {cuerpo}"
    
    def generar_codigo(self):
        codigo = []
        if self.nombre[1] != 'main':  # Solo generar etiqueta si no es main
            codigo.append(f'{self.nombre[1]}:')
            for i, param in enumerate(self.parametros):
                codigo.append(f'   mov eax, [esp+{4*(i+1)}]')
                codigo.append(f'   mov [{param.nombre[1]}], eax')
        
        # Generar código para el cuerpo
        for instruccion in self.cuerpo:
            codigo.append(instruccion.generar_codigo())
        
        if self.nombre[1] != 'main':
            codigo.append('   ret')
        
        return '\n'.join(codigo)

class NodoParametro(NodoAST):
    # Nodo que representa un parámetro de función
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

    def __repr__(self):
        return f"NodoParametro({self.nombre})"


class NodoAsignacion(NodoAST):
    # Nodo que representa una asignación de variable
    def __init__(self, nombre, expresion):
        self.nombre = nombre
        self.expresion = expresion

    def __repr__(self):
        return f"NodoAsignacion({self.nombre} = {self.expresion})"


    def generar_codigo(self):
        codigo = self.expresion.generar_codigo()
        codigo += f'\n   mov [{self.nombre[1]}], eax; Guardar resultado en {self.nombre[1]}'
        return codigo


class NodoOperacion(NodoAST):
    # Nodo que representa una operación aritmética
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

    def optimizar(self):
        if isinstance(self.izquierda, NodoOperacion):
            self.izquierda = self.izquierda.optimizar()
        else:
            izquierda = self.izquierda
        if isinstance(self.derecha, NodoOperacion):
            self.derecha = self.derecha.optimizar()
        else:
            derecha = self.derecha

        # Si ambos operandos son números, evaluamos la operación
        if isinstance(izquierda, NodoNumero) and isinstance(derecha, NodoNumero):
            if self.operador == "+":
                return NodoNumero(izquierda.valor + derecha.valor)
            elif self.operador == "-":
                return NodoNumero(izquierda.valor - derecha.valor)
            elif self.operador == "*":
                return NodoNumero(izquierda.valor * derecha.valor)
            elif self.operador == "/" and derecha.valor != 0:
                return NodoNumero(izquierda.valor / derecha.valor)
        # Simplificación algebraica
        if self.operador == '*' and isinstance(derecha, NodoNumero) and derecha.valor == 1:
            return izquierda
        if self.operador == '*' and isinstance(izquierda, NodoNumero) and izquierda.valor == 1:
            return derecha
        if self.operador == '+' and isinstance(derecha, NodoNumero) and derecha.valor == 0:
            return izquierda
        if self.operador == '+' and isinstance(izquierda, NodoNumero) and izquierda.valor == 0:
            return derecha

        return NodoOperacion(izquierda, self.operador, derecha)
        
    def __repr__(self):
        return f"({self.izquierda} {self.operador} {self.derecha})"
    
    def generar_codigo(self):
        codigo = []
        codigo.append(self.izquierda.generar_codigo()) # Cargar el operando izquierdo
        codigo.append('   push eax; guardar en la pila') # Guardar en la pila
        codigo.append(self.derecha.generar_codigo()) # Cargar el operando derecho
        codigo.append('   pop ebx; recuperar el primer operando') # Sacar de la pila
        # ebx = op1 y eax = op2
        if self.operador[1] == '+':
            codigo.append('   add eax, ebx; eax = eax + ebx')
        elif self.operador[1] == '-':
            codigo.append('   sub ebx, eax; ebx = ebx - eax')
            codigo.append('   mov eax, ebx; eax = ebx')
        elif self.operador[1] == '*':
            codigo.append('   imul ebx; eax = eax * ebx')
        elif self.operador[1] == '/':
            codigo.append('   mov edx, 0; limpiar edx')
            codigo.append('   idiv ebx; eax = eax / ebx')
        elif self.operador[1] == '<':
            codigo.append('   cmp eax, ebx; comparar eax y ebx')
            codigo.append('   mov eax, 0; cargar 0 en eax')
            codigo.append('   setl al; eax = eax < ebx')
        elif self.operador[1] == '>':
            codigo.append('   cmp eax, ebx; comparar eax y ebx')
            codigo.append('   mov eax, 0; cargar 0 en eax')
            codigo.append('   setg al; eax = eax > ebx')
        return '\n'.join(codigo)

class NodoRetorno(NodoAST):
    # Nodo que representa a la sentencia return
    def __init__(self, expresion):
        self.expresion = expresion
        
    def __repr__(self):
        return f"NodoRetorno({self.expresion})"
    
    def generar_codigo(self):
        return self.expresion.generar_codigo() + '\n   ret ; Retornar desde la subrutina'

class NodoIdentificador(NodoAST):
    # Nodo que representa a un identificador
    def __init__(self, nombre):
        self.nombre = nombre

    def __repr__(self):
        return f"{self.nombre}"

    def generar_codigo(self):
        return f'   mov eax, [{self.nombre[1]}] ; Cargar variable {self.nombre[1]} en eax'

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor

    def traducir(self):
        return str(self.valor)
    
    def generar_codigo(self):
        return f'   mov eax, {self.valor} ; Cargar número {self.valor} en eax'

class NodoWhile(NodoAST):
    # Nodo que representa a un ciclo while
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo

    def generar_codigo(self):
        etiqueta_inicio = f'etiqueta_inicio'
        etiqueta_fin = f'etiqueta_fin_while'

        codigo = []
        codigo.append(f'{etiqueta_inicio}:')
        codigo.append(self.condicion.generar_codigo())
        codigo.append('   cmp eax, 0 ; Comparar resultado con 0')
        codigo.append(f'   jne {etiqueta_fin} ; Saltar al final si la condición es falsa')

        for instruccion in self.cuerpo:
            codigo.append(instruccion.generar_codigo())

        codigo.append(f'   jmp {etiqueta_inicio} ; Saltar al inicio del ciclo')
        codigo.append(f'{etiqueta_fin}:')

        return '\n'.join(codigo)

class NodoIf(NodoAST):
    # Nodo que representa una sentencia if
    def __init__(self, condicion, cuerpo, sino=None):
        self.condicion = condicion
        self.cuerpo = cuerpo
        self.sino = sino

    def generar_codigo(self):
        etiqueta_else = f'etiqueta_else'
        etiqueta_fin = f'etiqueta_fin_if'

        codigo = []
        codigo.append(self.condicion.generar_codigo())
        codigo.append('   cmp eax, 0 ; Comparar resultado con 0')

        if self.sino:
            codigo.append(f'   jne {etiqueta_else} ; Saltar a else si la condición es falsa')
        else:
            codigo.append(f'   je {etiqueta_fin} ; Saltar al final si la condición es falsa')

        # Código del cuerpo del if
        for instruccion in self.cuerpo:
            codigo.append(instruccion.generar_codigo())

        if self.sino:
            codigo.append(f'   jmp {etiqueta_fin} ; Saltar al final del if')
            codigo.append(f'{etiqueta_else}:')
            for instruccion in self.sino:
                codigo.append(instruccion.generar_codigo())

        codigo.append(f'{etiqueta_fin}:')
        return '\n'.join(codigo)
    

class NodoFor(NodoAST):
    def __init__(self, inicializacion, condicion, actualizacion, cuerpo):
        self.inicializacion = inicializacion  # Debe ser una NodoAsignacion
        self.condicion = condicion            # Expresión booleana
        self.actualizacion = actualizacion    # Debe ser una NodoAsignacion
        self.cuerpo = cuerpo

    def generar_codigo(self):
        etiqueta_inicio = "for_inicio"
        etiqueta_fin = "for_fin"
        
        codigo = []
        # Inicialización
        codigo.append(self.inicializacion.generar_codigo())
        
        # Etiqueta de inicio del bucle
        codigo.append(f"{etiqueta_inicio}:")
        
        # Condición
        codigo.append(self.condicion.generar_codigo())
        codigo.append("   cmp eax, 0")
        codigo.append(f"   jne {etiqueta_fin}")
        
        # Cuerpo del for, ejecuta todas las instrucciones dentro del for
        for instruccion in self.cuerpo:
            codigo.append(instruccion.generar_codigo())
        
        # Actualización, ejecuta la instrucción de actualización
        codigo.append(self.actualizacion.generar_codigo())
        
        # Salto al inicio del for
        codigo.append(f"   jmp {etiqueta_inicio}")
        
        # Etiqueta de fin
        codigo.append(f"{etiqueta_fin}:")
        
        return "\n".join(codigo)
    
    
class NodoPrint(NodoAST):
    # Nodo que representa a la función print
    def __init__(self, variable):
        self.variable = variable

    def generar_codigo(self):
            codigo = [
                self.variable.generar_codigo(),  # Obtener valor en eax",
                "   call imprimir"
            ]
            return "\n".join(codigo)

class NodoLlamadaFuncion(NodoAST):
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos

    def generar_codigo(self):
        codigo = []
        # Empujar argumentos en orden inverso
        for arg in reversed(self.argumentos):
            codigo.append(arg.generar_codigo())
            codigo.append("   push eax")
        
        codigo.append(f"   call {self.nombre[1]}")
        
        # Limpiar la pila (4 bytes por argumento)
        if self.argumentos:
            codigo.append(f"   add esp, {4*len(self.argumentos)}")
        
        return "\n".join(codigo)
    