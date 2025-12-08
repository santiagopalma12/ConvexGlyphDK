# ConvexGlyphDK

Juego educativo de trazado de palabras utilizando poligonos convexos y algoritmos geometricos avanzados.

## Descripcion
Este proyecto demuestra la implementacion de la **Jerarquia de Dobkin-Kirkpatrick** para la deteccion eficiente de intersecciones (log n) en un entorno interactivo con Pygame.

## Caracterasticas
- **Renderizado de Pologonos**: Generacion procedural de mallas para letras.
- **Algoritmo DK Hierarchy**: Estructura de datos espacial para consultas geometricas rapidas.
- **Interaccion de Corte**: Detecta si el trazo del mouse intersecta los poligonos.

## Instalacion
1. Instalar dependencias:
   `ash
   pip install -r requirements.txt
   `
2. Ejecutar el juego:
   `ash
   python main.py
   `

## Estructura del Proyecto
- src/dk_hierarchy.py: Implementacion del algoritmo Dobkin-Kirkpatrick.
- src/geometry.py: Primitivas geometricas y funciones auxiliares.
- src/letter_mesh.py: Generador de formas de letras.
- main.py: Bucle principal del juego.
