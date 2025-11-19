import pygame
import sys
from src.letter_mesh import generate_polygon_mesh

# Configuración inicial
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ConvexGlyph - Prototipo")
clock = pygame.time.Clock()

def main():
    # Generar una forma de prueba
    poly = generate_polygon_mesh('A', 100)
    poly = [(x + 400, y + 300) for x, y in poly] # Centrar

    while True:
        screen.fill((30, 30, 30))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Dibujar polígono
        pygame.draw.polygon(screen, (0, 255, 100), poly, 2)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
