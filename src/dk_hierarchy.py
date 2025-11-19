from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from src.geometry import bounds_overlap, polygon_bounds, segment_bounds, segment_hits_convex


VertexId = int
Face = Tuple[VertexId, VertexId, VertexId]


def _project(point: Tuple[float, ...]) -> Tuple[float, float]:
    if not point:
        return (0.0, 0.0)
    if len(point) == 1:
        return (point[0], 0.0)
    return (point[0], point[1])


def polyhedron_from_convex_polygon(points: Sequence[Tuple[float, float]]) -> "Polyhedron":
    if len(points) < 3:
        raise ValueError("A convex polygon needs at least three points")
    vertices = [tuple(map(float, p)) for p in points]
    faces: List[Face] = []
    for idx in range(1, len(points) - 1):
        faces.append((0, idx, idx + 1))
    return Polyhedron(vertices, faces)


@dataclass(frozen=True)
class ParentPointer:
    """Describes how a face in layer i+1 maps back to layer i."""

    kind: str  # "face" or "vertex"
    reference: int


@dataclass
class Polyhedron:
    """Triangulated convex polyhedron (or polygonal mesh) with adjacency helpers."""

    vertices: List[Tuple[float, ...]]
    faces: List[Face]

    def __post_init__(self) -> None:
        self.vertices = [tuple(v) for v in self.vertices]
        self.faces = [self._canonical_face(face) for face in self.faces]
        self._build_topology()

    # --- topology helpers -------------------------------------------------
    def _build_topology(self) -> None:
        self.vertex_neighbors: List[Set[VertexId]] = [set() for _ in self.vertices]
        self.vertex_faces: List[Set[int]] = [set() for _ in self.vertices]
        for face_index, face in enumerate(self.faces):
            a, b, c = face
            if len({a, b, c}) != 3:
                raise ValueError("Degenerate face detected")
            for u, v in ((a, b), (b, c), (c, a)):
                self.vertex_neighbors[u].add(v)
                self.vertex_neighbors[v].add(u)
            for vertex in face:
                self.vertex_faces[vertex].add(face_index)

    @staticmethod
    def _canonical_face(face: Sequence[VertexId]) -> Face:
        if len(face) != 3:
            raise ValueError("Faces must be triangles")
        return tuple(sorted(int(v) for v in face))  # type: ignore[return-value]

    # --- public queries ----------------------------------------------------
    @property
    def num_vertices(self) -> int:
        return len(self.vertices)

    def available_vertices(self) -> Iterable[VertexId]:
        return range(len(self.vertices))

    def degree(self, vertex: VertexId) -> int:
        return len(self.vertex_neighbors[vertex])

    def get_neighbors(self, vertex: VertexId) -> Tuple[VertexId, ...]:
        return tuple(sorted(self.vertex_neighbors[vertex]))

    def incident_faces(self, vertex: VertexId) -> Set[int]:
        return set(self.vertex_faces[vertex])

    def face_vertices(self, face_index: int) -> List[Tuple[float, ...]]:
        ids = self.faces[face_index]
        return [self.vertices[idx] for idx in ids]

    # --- hierarchy helpers -------------------------------------------------
    def maximal_independent_set(self, candidates: Iterable[VertexId]) -> List[VertexId]:
        blocked: Set[VertexId] = set()
        independent: List[VertexId] = []
        for vertex in sorted(candidates, key=self.degree):
            if vertex in blocked:
                continue
            if any(neigh in independent for neigh in self.vertex_neighbors[vertex]):
                continue
            independent.append(vertex)
            blocked.add(vertex)
            blocked.update(self.vertex_neighbors[vertex])
        return independent

    def create_next_layer(
        self,
        remove_vertices: Iterable[VertexId],
    ) -> Tuple["Polyhedron", List[ParentPointer]]:
        remove_set = set(remove_vertices)
        if not remove_set:
            raise ValueError("Expected at least one vertex to remove")
        face_info: Dict[Face, ParentPointer] = {}
        for face_index, face in enumerate(self.faces):
            if remove_set.intersection(face):
                continue
            face_info[face] = ParentPointer("face", face_index)
        for vertex in remove_set:
            ring = self._ordered_vertex_ring(vertex)
            if len(ring) < 3:
                continue
            anchor = ring[0]
            for i in range(1, len(ring) - 1):
                tri = self._canonical_face((anchor, ring[i], ring[i + 1]))
                face_info.setdefault(tri, ParentPointer("vertex", vertex))
        return self._reindexed(face_info, remove_set)

    def _ordered_vertex_ring(self, vertex: VertexId) -> List[VertexId]:
        neighbors = list(self.vertex_neighbors[vertex])
        if len(neighbors) < 3:
            return neighbors
        adjacency: Dict[VertexId, Set[VertexId]] = {n: set() for n in neighbors}
        for face_index in self.vertex_faces[vertex]:
            face = self.faces[face_index]
            others = [idx for idx in face if idx != vertex]
            if len(others) != 2:
                continue
            a, b = others
            adjacency[a].add(b)
            adjacency[b].add(a)
        start = neighbors[0]
        ordered: List[VertexId] = []
        prev = None
        current = start
        for _ in range(len(neighbors)):
            ordered.append(current)
            next_candidates = adjacency[current] - ({prev} if prev is not None else set())
            if not next_candidates:
                break
            nxt = next(iter(sorted(next_candidates)))
            prev, current = current, nxt
            if current == start:
                break
        if len(ordered) != len(neighbors):
            remaining = [n for n in neighbors if n not in ordered]
            ordered.extend(remaining)
        return ordered

    def _reindexed(
        self,
        faces: Dict[Face, ParentPointer],
        removed: Set[VertexId],
    ) -> Tuple["Polyhedron", List[ParentPointer]]:
        index_map: Dict[VertexId, VertexId] = {}
        new_vertices: List[Tuple[float, ...]] = []
        for idx, point in enumerate(self.vertices):
            if idx in removed:
                continue
            index_map[idx] = len(new_vertices)
            new_vertices.append(point)
        new_faces: List[Face] = []
        parent_links: List[ParentPointer] = []
        for face, pointer in faces.items():
            mapped = tuple(sorted(index_map[v] for v in face))
            if len({mapped[0], mapped[1], mapped[2]}) != 3:
                continue
            new_faces.append(mapped)
            parent_links.append(pointer)
        return Polyhedron(new_vertices, new_faces), parent_links


@dataclass
class HierarchyLevel:
    mesh: Polyhedron
    parents: Optional[List[ParentPointer]] = None
    bbox: Optional[Tuple[float, float, float, float]] = None
    face_bboxes: Optional[List[Tuple[float, float, float, float]]] = None


class DKHierarchy:
    """Dobkin-Kirkpatrick hierarchy for convex polyhedra."""

    def __init__(self, levels: List[HierarchyLevel]):
        if not levels:
            raise ValueError("Hierarchy requires at least one layer")
        self.levels = levels
        self._prepare_bounds()

    @classmethod
    def build(
        cls,
        polyhedron: Polyhedron,
        degree_limit: int = 11,
    ) -> "DKHierarchy":
        levels = [HierarchyLevel(polyhedron, parents=None)]
        current = polyhedron
        current_limit = degree_limit
        while current.num_vertices > 4:
            candidates = [v for v in current.available_vertices() if current.degree(v) <= current_limit]
            if not candidates:
                current_limit += 1
                continue
            independent = current.maximal_independent_set(candidates)
            if not independent:
                current_limit += 1
                continue
            next_layer, parents = current.create_next_layer(independent)
            if next_layer.num_vertices == current.num_vertices:
                current_limit += 1
                continue
            levels.append(HierarchyLevel(next_layer, parents))
            current = next_layer
            current_limit = degree_limit
        return cls(levels)

    def height(self) -> int:
        return len(self.levels)

    def __iter__(self):
        return (level.mesh for level in self.levels)

    def __len__(self) -> int:
        return len(self.levels)

    def top(self) -> Polyhedron:
        return self.levels[0].mesh

    def apex(self) -> Polyhedron:
        return self.levels[-1].mesh

    def level(self, index: int) -> HierarchyLevel:
        return self.levels[index]

    # --- queries ----------------------------------------------------------
    def intersects_segment(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
    ) -> bool:
        if not self.levels:
            return False
        seg_bounds = segment_bounds(start, end)
        stack: List[Tuple[int, Optional[ParentPointer]]] = [(len(self.levels) - 1, None)]
        while stack:
            level_idx, constraint = stack.pop()
            level = self.levels[level_idx]
            if level.bbox and not bounds_overlap(seg_bounds, level.bbox):
                continue
            face_indices = self._faces_to_check(level_idx, constraint)
            face_bboxes = level.face_bboxes or []
            for face_idx in face_indices:
                if face_idx < 0 or face_idx >= len(level.mesh.faces):
                    continue
                if face_bboxes and not bounds_overlap(seg_bounds, face_bboxes[face_idx]):
                    continue
                polygon = [_project(v) for v in level.mesh.face_vertices(face_idx)]
                if not segment_hits_convex(start, end, polygon):
                    continue
                if level_idx == 0:
                    return True
                pointer = level.parents[face_idx] if level.parents else None
                if pointer is None:
                    return True
                stack.append((level_idx - 1, pointer))
        return False

    def _faces_to_check(
        self,
        level_idx: int,
        pointer: Optional[ParentPointer],
    ) -> Iterable[int]:
        mesh = self.levels[level_idx].mesh
        if pointer is None:
            return range(len(mesh.faces))
        if pointer.kind == "face":
            return [pointer.reference]
        if pointer.kind == "vertex":
            return list(mesh.incident_faces(pointer.reference))
        return range(len(mesh.faces))

    # --- preprocessing ----------------------------------------------------
    def _prepare_bounds(self) -> None:
        for level in self.levels:
            level.bbox = self._mesh_bounds(level.mesh)
            level.face_bboxes = [self._face_bounds(level.mesh, idx) for idx in range(len(level.mesh.faces))]

    @staticmethod
    def _mesh_bounds(mesh: Polyhedron) -> Tuple[float, float, float, float]:
        if not mesh.vertices:
            return (0.0, 0.0, 0.0, 0.0)
        xs = [ _project(v)[0] for v in mesh.vertices ]
        ys = [ _project(v)[1] for v in mesh.vertices ]
        return (min(xs), min(ys), max(xs), max(ys))

    @staticmethod
    def _face_bounds(mesh: Polyhedron, face_index: int) -> Tuple[float, float, float, float]:
        points = [_project(v) for v in mesh.face_vertices(face_index)]
        return polygon_bounds(points)
