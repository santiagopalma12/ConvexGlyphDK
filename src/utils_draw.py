# src/utils_draw.py
import pygame

def draw_grid(surface, width, height, camera_x):
    offset_x = int(camera_x) % 50 
    for x in range(-offset_x, width, 50):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, height))
    for y in range(0, height, 50):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (width, y))

def draw_scrollbar(surface, camera_x, total_width, screen_width, screen_height):
    if total_width <= screen_width: return
    bar_y = screen_height - 15
    pygame.draw.rect(surface, (40, 40, 40), (0, bar_y, screen_width, 10))
    
    view_ratio = screen_width / total_width
    thumb_width = max(50, screen_width * view_ratio)
    scrollable = total_width - screen_width
    if scrollable <= 0: scrollable = 1
    
    thumb_x = (camera_x / scrollable) * (screen_width - thumb_width)
    pygame.draw.rect(surface, (150, 150, 150), (thumb_x, bar_y, thumb_width, 10), border_radius=5)

def draw_debug_trace(surface, trace, font_trace):
    if not trace: return
    PANEL_W = 350
    PANEL_X = surface.get_width() - PANEL_W
    s = pygame.Surface((PANEL_W, surface.get_height()))
    s.set_alpha(230)
    s.fill((20, 20, 30))
    surface.blit(s, (PANEL_X, 0))
    
    title = font_trace.render("DK Trace", True, (255, 255, 255))
    surface.blit(title, (PANEL_X + 20, 20))
    
    y_offset = 60
  
    font_small = pygame.font.SysFont('Consolas', 12)
    
    for i, (level_idx, polygon, hit) in enumerate(trace):
        if y_offset > surface.get_height() - 50: break
        step_height = 90
        rect = pygame.Rect(PANEL_X + 20, y_offset, PANEL_W - 40, step_height)
        pygame.draw.rect(surface, (40, 40, 50), rect, border_radius=5)
        
        status_color = (100, 255, 100) if hit else (255, 100, 100)
        pygame.draw.rect(surface, status_color, rect, 2, border_radius=5)
        
        surface.blit(font_small.render(f"Nivel: {level_idx}", True, (200,200,200)), (rect.x + 10, rect.y + 10))
        surface.blit(font_small.render(f"Result: {'HIT' if hit else 'MISS'}", True, status_color), (rect.x + 10, rect.y + 50))
        y_offset += step_height + 10