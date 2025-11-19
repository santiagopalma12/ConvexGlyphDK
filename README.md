# Intersección de Polígonos y Jerarquía Dobkin-Kirkpatrick

Este repositorio contiene dos componentes complementarios:

1. **Convex Intersection Trainer** (`main.py`): un prototipo interactivo en Pygame donde las letras están formadas por polígonos convexos. Cada polígono construye una jerarquía de Dobkin-Kirkpatrick para validar los trazos del usuario en tiempo casi logarítmico.
2. **Jerarquía Dobkin-Kirkpatrick** (`src/dk_hierarchy.py`): una implementación reutilizable de la estructura jerárquica para poliedros/mallas trianguladas descrita por Dobkin y Kirkpatrick (1985), con soporte para enlaces padre-hijo entre capas y consultas de segmento.

## Requisitos

Instala las dependencias base (solo `pygame` hasta ahora):

```powershell
python -m pip install -r requirements.txt
```

## Ejecutar el juego en pantalla completa

```powershell
python main.py
```

## Construir la jerarquía DK de ejemplo

El script `dk_demo.py` genera un octaedro y crea la jerarquía completa, mostrando cuántos vértices/caraspersisten en cada nivel.

```powershell
python dk_demo.py
```

La demo ahora también ejecuta un par de consultas `intersects_segment` contra la jerarquía construida.

## Uso del módulo `dk_hierarchy`

```python
from src.dk_hierarchy import DKHierarchy, Polyhedron

poly = Polyhedron(vertices=[...], faces=[...])  # malla triangulada convexa
hierarchy = DKHierarchy.build(poly)
print(f"Altura logarítmica: {hierarchy.height()} niveles")
print(hierarchy.intersects_segment((0.0, -2.0), (0.0, 2.0)))
```

Cada `HierarchyLevel` expone:

- `mesh`: la malla simplificada `P_i`.
- `parents`: lista de `ParentPointer` que indica si cada cara proviene directamente de una cara del nivel anterior o si fue creada al eliminar un vértice.

Esto facilita añadir algoritmos de localización de puntos o recorridos top-down usando los punteros de padres.
