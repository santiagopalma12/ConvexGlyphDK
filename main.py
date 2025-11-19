import pygame
import sys
from src.letter_mesh import generate_polygon_mesh
from src.geometry import is_point_in_polygon

# Configuración inicial
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ConvexGlyph - Prototipo")
clock = pygame.time.Clock()

class PolygonGoal:
    def __init__(self, char, x, y, scale=50):
        self.char = char
        raw_poly = generate_polygon_mesh(char, scale)
        self.vertices = [(px + x, py + y) for px, py in raw_poly]
        self.hovered = False
        self.completed = False

    def update(self, mouse_pos):
        if self.completed: return
        self.hovered = is_point_in_polygon(mouse_pos, self.vertices)

    def draw(self, surface):
        color = (0, 255, 0) if self.completed else ((255, 255, 0) if self.hovered else (100, 100, 255))
        pygame.draw.polygon(surface, color, self.vertices, 3)

def main():
    goal = PolygonGoal('A', 400, 300, 100)

    while True:
        screen.fill((30, 30, 30))
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if goal.hovered:
                    goal.completed = True
        
        goal.update(mouse_pos)
        goal.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
