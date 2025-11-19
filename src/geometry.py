import math

def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def cross(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def sub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def add(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])
