# ConvexGlyphDK

Juego educativo de trazado de palabras utilizando poligonos convexos y algoritmos geometricos avanzados.

## Descripci�n
Este proyecto demuestra la implementaci�n de la **Jerarqu�a de Dobkin-Kirkpatrick** para la detecci�n eficiente de intersecciones ((\log n)$) en un entorno interactivo con Pygame.

## Caracter�sticas
- **Renderizado de Pol�gonos**: Generaci�n procedural de mallas para letras.
- **Algoritmo DK Hierarchy**: Estructura de datos espacial para consultas geom�tricas r�pidas.
- **Interacci�n de Corte**: Detecta si el trazo del mouse intersecta los pol�gonos.

## Instalaci�n
1. Instalar dependencias:
   `ash
   pip install -r requirements.txt
   `
2. Ejecutar el juego:
   `ash
   python main.py
   `

## Estructura del Proyecto
- src/dk_hierarchy.py: Implementaci�n del algoritmo Dobkin-Kirkpatrick.
- src/geometry.py: Primitivas geom�tricas y funciones auxiliares.
- src/letter_mesh.py: Generador de formas de letras.
- main.py: Bucle principal del juego.
