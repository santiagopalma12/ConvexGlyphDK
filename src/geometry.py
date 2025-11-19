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
