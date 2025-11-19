import pygame
import sys
from src.letter_mesh import generate_polygon_mesh
from src.dk_hierarchy import polyhedron_from_convex_polygon, DKHierarchy

# Configuración inicial
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ConvexGlyph - DK Intersection")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont('Arial', 30)

# Placeholder para sonidos
try:
    CLICK_SOUND = pygame.mixer.Sound('assets/click.wav')
except:
    CLICK_SOUND = None

def draw_grid(surface):
    for x in range(0, WIDTH, 50):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (WIDTH, y))

class PolygonGoal:
    def __init__(self, char, x, y, scale=50):
        self.char = char
        raw_poly = generate_polygon_mesh(char, scale)
        self.vertices = [(px + x, py + y) for px, py in raw_poly]
        self.completed = False
        self.highlight = False
        
        # Construir Jerarquía DK
        poly = polyhedron_from_convex_polygon(self.vertices)
        self.hierarchy = DKHierarchy.build(poly)

    def update(self, last_pos, curr_pos, is_clicking):
        if self.completed: return
        
        # Detectar intersección usando DK Hierarchy (O(log n))
        # Si el segmento del mouse cruza el polígono, se activa
        if self.hierarchy.intersects_segment(last_pos, curr_pos):
            self.highlight = True
            if is_clicking:
                self.completed = True
                if CLICK_SOUND: CLICK_SOUND.play()
        else:
            self.highlight = False

    def draw(self, surface):
        color = (0, 255, 0) if self.completed else ((255, 255, 0) if self.highlight else (100, 100, 255))
        pygame.draw.polygon(surface, color, self.vertices, 3)

class WordGoal:
    def __init__(self, word, start_x, y, scale=50):
        self.polygons = []
        offset = 0
        for char in word:
            self.polygons.append(PolygonGoal(char, start_x + offset, y, scale))
            offset += scale * 1.5

    def update(self, last_pos, curr_pos, is_clicking):
        for poly in self.polygons:
            poly.update(last_pos, curr_pos, is_clicking)

    def draw(self, surface):
        for poly in self.polygons:
            poly.draw(surface)

def main():
    word_goal = WordGoal("HOLA", 300, 300, 80)
    last_pos = pygame.mouse.get_pos()

    while True:
        screen.fill((30, 30, 30))
        draw_grid(screen)
        
        curr_pos = pygame.mouse.get_pos()
        is_clicking = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        word_goal.update(last_pos, curr_pos, is_clicking)
        word_goal.draw(screen)
        
        # Dibujar rastro del mouse
        if is_clicking:
            pygame.draw.line(screen, (255, 0, 0), last_pos, curr_pos, 2)
            
        last_pos = curr_pos
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
