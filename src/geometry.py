import math

def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def cross(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def sub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def add(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def is_point_in_polygon(point, polygon):
    # Algoritmo simple de Ray Casting (Even-Odd rule)
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# --- Funciones avanzadas para DK Hierarchy ---

def polygon_bounds(poly):
    if not poly: return (0,0,0,0)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))

def bounds_overlap(b1, b2):
    # b = (minx, miny, maxx, maxy)
    return not (b1[2] < b2[0] or b1[0] > b2[2] or b1[3] < b2[1] or b1[1] > b2[3])

def segment_bounds(p1, p2):
    return (min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1]))

def segment_hits_convex(p1, p2, poly):
    # Implementación simplificada: verificar si algún punto está dentro o si cruza bordes
    if is_point_in_polygon(p1, poly) or is_point_in_polygon(p2, poly):
        return True
    # Chequeo de intersección de segmentos
    n = len(poly)
    for i in range(n):
        edge_p1 = poly[i]
        edge_p2 = poly[(i + 1) % n]
        if segments_intersect(p1, p2, edge_p1, edge_p2):
            return True
    return False

def segments_intersect(a, b, c, d):
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    return ccw(a,c,d) != ccw(b,c,d) and ccw(a,b,c) != ccw(a,b,d)
