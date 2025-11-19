from __future__ import annotations

from src.dk_hierarchy import DKHierarchy, Polyhedron


def make_octahedron() -> Polyhedron:
    vertices = [
        (1.0, 0.0, 0.0),
        (-1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, -1.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.0, 0.0, -1.0),
    ]
    faces = [
        (0, 2, 4),
        (2, 1, 4),
        (1, 3, 4),
        (3, 0, 4),
        (2, 0, 5),
        (1, 2, 5),
        (3, 1, 5),
        (0, 3, 5),
    ]
    return Polyhedron(vertices, faces)


def main() -> None:
    poly = make_octahedron()
    hierarchy = DKHierarchy.build(poly)
    for level_index, level in enumerate(hierarchy.levels):
        mesh = level.mesh
        parent_summary = "base" if level.parents is None else f"{len(level.parents)} parent links"
        print(f"Nivel {level_index}: {mesh.num_vertices} vértices, {len(mesh.faces)} caras, {parent_summary}")

    tests = [
        (((-2.0, 0.0), (2.0, 0.0)), True),
        (((2.0, 2.0), (3.0, 3.0)), False),
    ]
    for (a, b), expected in tests:
        hit = hierarchy.intersects_segment(a, b)
        print(f"Segmento {a}->{b} intersecta: {hit} (esperado {expected})")


if __name__ == "__main__":
    main()
