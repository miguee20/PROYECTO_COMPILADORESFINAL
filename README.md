# PROYECTO_COMPILADORESFINAL

# Diagrama de Flujo a Código C y ASM (Compiladores)

## Integrantes del Proyecto
- Miguel Salguero
- Karen Laines
- Josue Orozco
- Julio Cáceres

## Descripción del Proyecto
Este proyecto es una herramienta visual para crear diagramas de flujo y convertirlos automáticamente a código en C y ensamblador (ASM). Está diseñado como parte de un curso de compiladores y permite:

- Crear diagramas de flujo con bloques estándar (inicio, fin, proceso, decisión, entrada/salida)
- Conectar bloques mediante interfaz gráfica
- Generar código C equivalente al diagrama
- Traducir el código C a ensamblador (ASM)
- Validar la sintaxis del diagrama
- Guardar/cargar diagramas en formato JSON

## Características Principales
- Interfaz gráfica intuitiva con canvas para dibujar diagramas
- Generación de código C con detección de estructuras (if-else, while, for)
- Traducción a ASM compatible con EMU8086
- Validación sintáctica de los bloques
- Sistema de zoom para trabajar con diagramas grandes
- Persistencia mediante guardado/recuperación de diagramas

## Requisitos
- **Python 3.x**
- Bibliotecas:
  - tkinter (incluida en Python)
  - json (incluida en Python)
  - os (incluida en Python)
  - re (incluida en Python)

## Instalación y Uso

### Instalación
git clone https://github.com/tu-usuario/PROYECTO_COMPILADORESFINAL.git
cd PROYECTO_COMPILADORESFINAL

# EJECUCIÓN
python conversor_a_C_10.py

# USO BÁSICO
- Botones superiores: agregar bloques al diagrama
- Arrastrar bloques para moverlos
- Click en puertos (puntos negros) para conectar bloques
- Doble click en un bloque para editarlo
- Ctrl + Rueda del mouse para hacer zoom

# EJEMPLO DE USO
1. Crear diagrama: inicio → entrada → proceso → decisión → salida → fin
2. Conectar bloques arrastrando desde los puertos
3. Click en "Generar C" para ver código equivalente
4. Validar diagrama con el botón correspondiente
5. Guardar diagrama para uso futuro

# Uso de diagramas creados
Ya que el programa lee los diagramas como archivos json, los diagramas de ejemplo guardados en la carpeta "proyecto_compiladores" son funcionales.
