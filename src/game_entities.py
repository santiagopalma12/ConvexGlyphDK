# src/game_entities.py
import pygame
from src.letter_mesh import generate_polygon_mesh
from src.dk_hierarchy import polyhedron_from_convex_polygon, DKHierarchy

class PixelGoal:
    def __init__(self, vertices):
        self.vertices = vertices 
        self.completed = False
        self.highlight = False
        poly = polyhedron_from_convex_polygon(self.vertices)
        self.hierarchy = DKHierarchy.build(poly)
    
    def check_collision(self, last_pos, curr_pos):
        return self.hierarchy.intersects_segment(last_pos, curr_pos)

    def update(self, last_pos_world, curr_pos_world, is_clicking):
        if self.completed: return False
        
        if self.check_collision(last_pos_world, curr_pos_world):
            self.highlight = True
            if is_clicking:
                self.completed = True
                return True
        else:
            self.highlight = False
        return False
    
    def get_debug_trace(self, last_pos_world, curr_pos_world):
        return self.hierarchy.trace_intersection(last_pos_world, curr_pos_world)

class LetterGoal:
    def __init__(self, char, x, y, scale=50):
        self.char = char
        raw_polys = generate_polygon_mesh(char, scale)
        self.pixels = []
        for raw_poly in raw_polys:
            vertices = [(px + x, py + y) for px, py in raw_poly]
            self.pixels.append(PixelGoal(vertices))
        
    def update(self, last_pos, curr_pos, is_clicking, sound_effect=None):
        hit_any = False
        for pixel in self.pixels:
            if pixel.update(last_pos, curr_pos, is_clicking):
                hit_any = True
        if hit_any and sound_effect:
            sound_effect.play()

    def is_completed(self):
        return all(pixel.completed for pixel in self.pixels)

class WordGoal:
    def __init__(self, word, start_y, screen_width, scale=50):
        self.polygons = []
        letter_spacing = scale * 1.5 
        word_spacing = scale * 1.0
        
        calculated_width = 0
        for char in word:
            if char == ' ': calculated_width += word_spacing
            else: calculated_width += letter_spacing
        
        if calculated_width < screen_width:
            start_x = (screen_width - calculated_width) // 2
        else:
            start_x = 50

        current_x = start_x
        for char in word:
            if char == ' ':
                current_x += word_spacing
            else:
                self.polygons.append(LetterGoal(char, current_x, start_y, scale))
                current_x += letter_spacing
            
        self.total_width = max(calculated_width + 100, screen_width)

    def update(self, last_pos, curr_pos, is_clicking, sound_effect=None):
        for poly in self.polygons:
            poly.update(last_pos, curr_pos, is_clicking, sound_effect)

    def is_inside_valid_area(self, curr_pos_world):
        p1 = curr_pos_world
        p2 = (curr_pos_world[0] + 0.1, curr_pos_world[1] + 0.1)
        for letter in self.polygons:
            for pixel in letter.pixels:
                if pixel.check_collision(p1, p2):
                    return True
        return False

    def is_completed(self):
        return all(poly.is_completed() for poly in self.polygons)
    
    def get_progress(self):
        total = 0
        comp = 0
        for letter in self.polygons:
            for pixel in letter.pixels:
                total += 1
                if pixel.completed: comp += 1
        return (comp / total) * 100 if total > 0 else 0

    def draw(self, surface, camera_x):
        for letter in self.polygons:
            for pixel in letter.pixels:
                screen_vertices = [(v[0] - camera_x, v[1]) for v in pixel.vertices]
                if any(-50 < v[0] < surface.get_width() + 50 for v in screen_vertices):
                    color = (0, 255, 0) if pixel.completed else ((255, 255, 0) if pixel.highlight else (100, 100, 255))
                    pygame.draw.polygon(surface, color, screen_vertices, 0)
                    pygame.draw.polygon(surface, (50, 50, 50), screen_vertices, 1)

def get_closest_pixel(word_goal, pos_world):
    closest = None
    min_dist = float('inf')
    for letter in word_goal.polygons:
        for pixel in letter.pixels:
            cx = sum(v[0] for v in pixel.vertices) / len(pixel.vertices)
            cy = sum(v[1] for v in pixel.vertices) / len(pixel.vertices)
            dist = (cx - pos_world[0])**2 + (cy - pos_world[1])**2
            if dist < min_dist:
                min_dist = dist
                closest = pixel
    return closest