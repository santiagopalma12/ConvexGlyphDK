import pygame
import sys
from src.letter_mesh import generate_polygon_mesh
from src.geometry import is_point_in_polygon

# Configuración inicial
pygame.init()
pygame.mixer.init() # Inicializar sonido
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ConvexGlyph - Prototipo")
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
        self.hovered = False
        self.completed = False

    def update(self, mouse_pos):
        if self.completed: return
        self.hovered = is_point_in_polygon(mouse_pos, self.vertices)

    def draw(self, surface):
        color = (0, 255, 0) if self.completed else ((255, 255, 0) if self.hovered else (100, 100, 255))
        pygame.draw.polygon(surface, color, self.vertices, 3)

class WordGoal:
    def __init__(self, word, start_x, y, scale=50):
        self.polygons = []
        offset = 0
        for char in word:
            self.polygons.append(PolygonGoal(char, start_x + offset, y, scale))
            offset += scale * 1.5

    def update(self, mouse_pos):
        for poly in self.polygons:
            poly.update(mouse_pos)

    def check_click(self):
        for poly in self.polygons:
            if poly.hovered and not poly.completed:
                poly.completed = True
                if CLICK_SOUND: CLICK_SOUND.play()

    def draw(self, surface):
        for poly in self.polygons:
            poly.draw(surface)

def main():
    word_goal = WordGoal("HOLA", 300, 300, 80)

    while True:
        screen.fill((30, 30, 30))
        draw_grid(screen)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                word_goal.check_click()
        
        word_goal.update(mouse_pos)
        word_goal.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
