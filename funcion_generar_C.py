def generar_codigo_c(diagrama):
    codigo = "#include <stdio.h>\n\nint main() {\n"
    indent = "    "
    variables_declaradas = set()
    cuerpo_codigo = ""
    pila_estructuras = []  # Para manejar anidamiento (if/for/while)

    # Declaración automática de variables típicas
    variables_posibles = ["i", "n", "numero", "suma", "contador"]

    # Función para declarar variables si no existen
    def declarar_variable(var):
        nonlocal cuerpo_codigo
        if var not in variables_declaradas:
            cuerpo_codigo += f"{indent * len(pila_estructuras)}int {var};\n"
            variables_declaradas.add(var)

    # Procesamos cada bloque del diagrama
    for bloque in diagrama:
        indent_actual = indent * len(pila_estructuras)

        # --- DECLARACIONES / ENTRADA ---
        if bloque.tipo == "entrada":
            declarar_variable(bloque.contenido)
            cuerpo_codigo += f"{indent_actual}scanf(\"%d\", &{bloque.contenido});\n"

        # --- PROCESO (ASIGNACIONES) ---
        elif bloque.tipo == "proceso":
            # Detectar asignaciones como "i = 0"
            if "=" in bloque.contenido:
                var = bloque.contenido.split("=")[0].strip()
                declarar_variable(var)
            cuerpo_codigo += f"{indent_actual}{bloque.contenido};\n"

        # --- DECISIÓN (IF / ELSE) ---
        elif bloque.tipo == "decision":
            condicion = bloque.contenido
            cuerpo_codigo += f"{indent_actual}if ({condicion}) {{\n"
            pila_estructuras.append("if")  # Marcamos que estamos en un if

        # --- CIERRE DE ESTRUCTURAS (LLAVES) ---
        # (Asumimos que hay un bloque "fin" o conexiones que indican el final)
        elif bloque.tipo == "fin" and pila_estructuras:
            estructura = pila_estructuras.pop()
            if estructura in ["if", "else", "for", "while"]:
                cuerpo_codigo += f"{indent * len(pila_estructuras)}}}\n"
            elif estructura == "else":
                cuerpo_codigo += f"{indent * len(pila_estructuras)}}}\n"

    # --- DECLARAMOS VARIABLES NO USADAS AL INICIO ---
    vars_a_declarar = [v for v in variables_posibles if v in variables_declaradas]
    declaraciones_iniciales = ""
    for var in vars_a_declarar:
        declaraciones_iniciales += f"{indent}int {var};\n"

    # --- CONSTRUIMOS EL CÓDIGO FINAL ---
    codigo = "#include <stdio.h>\n\nint main() {\n" + declaraciones_iniciales + cuerpo_codigo + "    return 0;\n}\n"
    return codigo