# ConvexGlyphDK

Juego educativo de trazado de palabras utilizando polígonos convexos y algoritmos geométricos avanzados.

## Descripción
Este proyecto demuestra la implementación de la **Jerarquía de Dobkin-Kirkpatrick** para la detección eficiente de intersecciones ((\log n)$) en un entorno interactivo con Pygame.

## Características
- **Renderizado de Polígonos**: Generación procedural de mallas para letras.
- **Algoritmo DK Hierarchy**: Estructura de datos espacial para consultas geométricas rápidas.
- **Interacción de Corte**: Detecta si el trazo del mouse intersecta los polígonos.

## Instalación
1. Instalar dependencias:
   `ash
   pip install -r requirements.txt
   `
2. Ejecutar el juego:
   `ash
   python main.py
   `

## Estructura del Proyecto
- src/dk_hierarchy.py: Implementación del algoritmo Dobkin-Kirkpatrick.
- src/geometry.py: Primitivas geométricas y funciones auxiliares.
- src/letter_mesh.py: Generador de formas de letras.
- main.py: Bucle principal del juego.
