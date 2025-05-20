from analizador import *
#------------------------- Análisis semántico -------------------------
class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
    
    def analizar(self, nodo):
        if isinstance(nodo, NodoAsignacion):
            tipo_expr = self.analizar(nodo.expresion)
            self.tabla_simbolos.declarar_variable(nodo.nombre, tipo_expr)

        elif isinstance(nodo, NodoIdentificador):
            return self.tabla_simbolos.obtener_tipo_variable(nodo.nombre)
        
        elif isinstance(nodo, NodoNumero):
            return "int"
        
        elif isinstance(nodo, NodoOperacion):
            tipo_izq = self.analizar(nodo.izquierda)
            tipo_der = self.analizar(nodo.derecha)
            if tipo_izq != tipo_der:
                raise Exception(f"Error: Tipos incompatibles en operacion '{tipo_izq} {nodo.operador} {tipo_der}'")
            return tipo_izq #Retorna el tipo resultante
        
        elif isinstance(nodo, NodoFuncion):
            self.tabla_simbolos.declarar_funcion(nodo.nombre, nodo.tipo_retorno, nodo.parametros)
            for instruccion in nodo.cuerpo:
                self.analizar(instruccion)

        elif isinstance(nodo, NodoLlamadaFuncion):
            tipo_retorno, parametros = self.tabla_simbolos.obtener_info_funcion(nodo.nombre)
            if len(nodo.argumentos) != len(parametros):
                raise Exception(f"Error: La funcion '{nodo.nombre}' espera {len(parametros)} argumentos, pero recibio {len(nodo.argumentos)}")
            return tipo_retorno
        
        elif isinstance(nodo, NodoPrograma): 
            for funcion in nodo.funciones:
                self.analizar(funcion)
    
    # def visitar_NodoPrograma(self, nodo):
    #     # Programa contiene una lista de NodoFuncion
    #     for funcion in nodo.funciones:
    #         self.analizar(funcion)
        

    # def visitar_NodoFuncion(self, nodo):
    #     if nodo.nombre[1] in self.tabla_simbolos:
    #         raise Exception(f'Error semántico: la función {nodo.nombre[1]} ya está definida')
    #     self.tabla_simbolos[nodo.nombre[1]] = {'tipo': nodo.parametros[0].tipo[1], 
    #                                            'parametros': nodo.parametros}
    #     for param in nodo.parametros:
    #         self.tabla_simbolos[param.nombre[1]] = {'tipo':param.tipo[1]}
    #     for instruccion in nodo.cuerpo:
    #         self.analizar(instruccion)

class TablaSimbolos:
    def __init__(self):
        self.variables = {} #Almacena variables {nombre: tipo}
        self.funciones = {} #Almacena funciones {nombre_ (retorno [parametros])}

    def declarar_variable(self, nombre, tipo):
        if nombre in self.variables:
            raise Exception(f"Error: Variable '{nombre}' ya declarada")
        self.variables[nombre] = tipo

    def obtener_tipo_variable(self, nombre):
        if nombre not in self.variables:
            raise Exception(f"Error_ Variable '{nombre}' no declarada")
        return self.variables[nombre]
    
    def declarar_funcion(self, nombre, tipo_retorno, parametros):
        if nombre in self.funciones:
            raise Exception(f"Error: Funcion '{nombre}' ya declarada")
        self.funciones[nombre] = (tipo_retorno, parametros)

    def obtener_info_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: Funcion '{nombre}' no declarada")
        return self.funciones[nombre]
    

