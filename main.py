import pygame
import sys
<<<<<<< HEAD
=======
import math
from src.letter_mesh import generate_polygon_mesh
from src.dk_hierarchy import polyhedron_from_convex_polygon, DKHierarchy
>>>>>>> 5e108aa69be2ff7dba8bd92ebffa13cd1a68be79

from src.menu import GameMenu  
from src.game_entities import WordGoal, get_closest_pixel
from src.utils_draw import draw_grid, draw_scrollbar, draw_debug_trace

pygame.init()
pygame.mixer.init()
<<<<<<< HEAD

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("ConvexGlyph - CalliRehab Edition")
clock = pygame.time.Clock()

# --- FUENTES ---
FONT_LABEL = pygame.font.SysFont('Consolas', 24, bold=True)
if not FONT_LABEL: FONT_LABEL = pygame.font.SysFont('Courier New', 24, bold=True)
FONT_VALUE = pygame.font.SysFont('Arial', 30, bold=True)
FONT_BIG = pygame.font.SysFont('Arial', 60, bold=True)
FONT_INFO = pygame.font.SysFont('Arial', 20)

=======
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ConvexGlyph - DK Intersection (Brush Mode)")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont('Arial', 30)

# Configuración del Pincel (Brush)
BRUSH_RADIUS = 10
BRUSH_SAMPLES = 100  # Número de puntos para aproximar el círculo (Stress Test extremo)

# Placeholder para sonidos
>>>>>>> 5e108aa69be2ff7dba8bd92ebffa13cd1a68be79
try:
    CLICK_SOUND = pygame.mixer.Sound('assets/click.wav')
except:
    CLICK_SOUND = None

<<<<<<< HEAD
=======
def draw_grid(surface):
    for x in range(0, WIDTH, 50):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (WIDTH, y))

class PixelGoal:
    def __init__(self, vertices):
        self.vertices = vertices
        self.completed = False
        self.highlight = False
        # Construir Jerarquia DK para este pixel
        poly = polyhedron_from_convex_polygon(self.vertices)
        self.hierarchy = DKHierarchy.build(poly)
    
    def update(self, brush_center, is_clicking):
        if self.completed: return False
        
        # BRUSH MODE LOGIC:
        # En lugar de un solo segmento, verificamos 100 puntos alrededor del cursor.
        # Esto multiplica la carga por 100, demostrando la eficiencia de DK.
        
        cx, cy = brush_center
        hit_found = False
        
        # 1. Verificar el centro
        if self.hierarchy.intersects_segment((cx, cy), (cx, cy)):
             hit_found = True
        
        # 2. Verificar puntos del perímetro si no hemos encontrado hit
        if not hit_found:
            for i in range(BRUSH_SAMPLES):
                angle = (2 * math.pi * i) / BRUSH_SAMPLES
                px = cx + math.cos(angle) * BRUSH_RADIUS
                py = cy + math.sin(angle) * BRUSH_RADIUS
                
                # Usamos intersects_segment con start=end para simular point-in-polygon
                if self.hierarchy.intersects_segment((px, py), (px, py)):
                    hit_found = True
                    break
        
        if hit_found:
            self.highlight = True
            if is_clicking:
                self.completed = True
                return True # Hit
        else:
            self.highlight = False
        return False
    
    def get_debug_trace(self, last_pos, curr_pos):
        # Para debug, seguimos usando el trazo simple del centro
        return self.hierarchy.trace_intersection(last_pos, curr_pos)

class LetterGoal:
    def __init__(self, char, x, y, scale=50):
        self.char = char
        raw_polys = generate_polygon_mesh(char, scale)
        self.pixels = []
        for raw_poly in raw_polys:
            # Offset vertices
            vertices = [(px + x, py + y) for px, py in raw_poly]
            self.pixels.append(PixelGoal(vertices))
        
    def update(self, brush_center, is_clicking):
        hit_any = False
        for pixel in self.pixels:
            if pixel.update(brush_center, is_clicking):
                hit_any = True
        if hit_any and CLICK_SOUND:
            CLICK_SOUND.play()

    def is_completed(self):
        return all(pixel.completed for pixel in self.pixels)

    def draw(self, surface):
        for pixel in self.pixels:
            color = (0, 255, 0) if pixel.completed else ((255, 255, 0) if pixel.highlight else (100, 100, 255))
            pygame.draw.polygon(surface, color, pixel.vertices, 0) # Relleno
            pygame.draw.polygon(surface, (50, 50, 50), pixel.vertices, 1) # Borde

class WordGoal:
    def __init__(self, word, start_x, y, scale=50):
        self.polygons = []
        offset = 0
        for char in word:
            self.polygons.append(LetterGoal(char, start_x + offset, y, scale))
            offset += scale * 1.5

    def update(self, brush_center, is_clicking):
        for poly in self.polygons:
            poly.update(brush_center, is_clicking)

    def is_completed(self):
        return all(poly.is_completed() for poly in self.polygons)

    def draw(self, surface):
        for poly in self.polygons:
            poly.draw(surface)

def get_closest_pixel(word_goal, pos):
    closest = None
    min_dist = float('inf')
    for letter in word_goal.polygons:
        for pixel in letter.pixels:
            # Centroid approx
            cx = sum(v[0] for v in pixel.vertices) / len(pixel.vertices)
            cy = sum(v[1] for v in pixel.vertices) / len(pixel.vertices)
            dist = (cx - pos[0])**2 + (cy - pos[1])**2
            if dist < min_dist:
                min_dist = dist
                closest = pixel
    return closest

def draw_debug_trace(surface, trace):
    if not trace: return
    
    # Panel dimensions
    PANEL_W = 350
    PANEL_X = WIDTH - PANEL_W
    
    # Background
    s = pygame.Surface((PANEL_W, HEIGHT))
    s.set_alpha(240)
    s.fill((30, 30, 40))
    surface.blit(s, (PANEL_X, 0))
    
    # Title
    font_title = pygame.font.SysFont('Arial', 20, bold=True)
    font_info = pygame.font.SysFont('Consolas', 14)
    
    title = font_title.render("DK Algorithm Trace", True, (255, 255, 255))
    surface.blit(title, (PANEL_X + 20, 20))
    
    y_offset = 60
    
    # Draw each step
    for i, (level_idx, polygon, hit) in enumerate(trace):
        # Box for this step
        step_height = 100
        rect = pygame.Rect(PANEL_X + 20, y_offset, PANEL_W - 40, step_height)
        pygame.draw.rect(surface, (50, 50, 60), rect, border_radius=5)
        
        # Color based on hit/miss
        status_color = (100, 255, 100) if hit else (255, 100, 100)
        pygame.draw.rect(surface, status_color, rect, 2, border_radius=5)
        
        # Text Info
        level_text = font_info.render(f"Level {level_idx}", True, (200, 200, 200))
        verts_text = font_info.render(f"Vertices: {len(polygon)}", True, (150, 150, 150))
        status_text = font_info.render(f"Result: {'INTERSECT' if hit else 'MISS'}", True, status_color)
        
        surface.blit(level_text, (rect.x + 10, rect.y + 10))
        surface.blit(verts_text, (rect.x + 10, rect.y + 30))
        surface.blit(status_text, (rect.x + 10, rect.y + 50))
        
        # Mini-map of the polygon
        mini_rect = pygame.Rect(rect.x + 150, rect.y + 10, 140, 80)
        
        if len(polygon) > 2:
            # Normalize polygon to fit in mini_rect
            min_x = min(p[0] for p in polygon)
            max_x = max(p[0] for p in polygon)
            min_y = min(p[1] for p in polygon)
            max_y = max(p[1] for p in polygon)
            
            poly_w = max_x - min_x
            poly_h = max_y - min_y
            scale = min(mini_rect.width / (poly_w or 1), mini_rect.height / (poly_h or 1)) * 0.8
            
            center_x = mini_rect.centerx
            center_y = mini_rect.centery
            
            # Centroid of polygon
            poly_cx = (min_x + max_x) / 2
            poly_cy = (min_y + max_y) / 2
            
            mini_poly = []
            for px, py in polygon:
                nx = center_x + (px - poly_cx) * scale
                ny = center_y + (py - poly_cy) * scale
                mini_poly.append((nx, ny))
            
            pygame.draw.polygon(surface, status_color, mini_poly, 2)
            
            # Draw vertices points
            for p in mini_poly:
                pygame.draw.circle(surface, (255, 255, 255), (int(p[0]), int(p[1])), 2)
            
        # Draw arrow to next if not last
        if i < len(trace) - 1:
            center_bottom = (rect.centerx, rect.bottom)
            next_top = (rect.centerx, rect.bottom + 20)
            pygame.draw.line(surface, (100, 100, 100), center_bottom, next_top, 2)
            
        y_offset += step_height + 20

>>>>>>> 5e108aa69be2ff7dba8bd92ebffa13cd1a68be79
def main():
    global WIDTH, HEIGHT, screen
    menu = GameMenu(WIDTH, HEIGHT)
    game_state = "MENU"
    word_goal = None
    
    camera_x = 0
    camera_speed = 15
    last_pos_screen = pygame.mouse.get_pos()
    last_pos_world = (last_pos_screen[0], last_pos_screen[1])
    
<<<<<<< HEAD
=======
    def load_level(index):
        word = words[index % len(words)]
        # Centrar la palabra aproximadamente
        # scale=80, spacing approx 1.5 * scale = 120 per char
        total_width = len(word) * 120 
        start_x = (WIDTH - total_width) // 2
        return WordGoal(word, start_x, 300, 80)

    word_goal = load_level(current_word_index)
>>>>>>> 5e108aa69be2ff7dba8bd92ebffa13cd1a68be79
    debug_mode = False
    
    time_limit = None
    start_ticks = 0
    total_samples = 0
    valid_samples = 0
    final_precision = 0
    final_time = 0.0
    show_results = False

    game_start_timestamp = 0 

    while True:
<<<<<<< HEAD
        try:
            dt = clock.tick(60)
            curr_pos_screen = pygame.mouse.get_pos()
            is_clicking = pygame.mouse.get_pressed()[0]
            curr_pos_world = (curr_pos_screen[0] + camera_x, curr_pos_screen[1])
=======
        screen.fill((30, 30, 30))
        draw_grid(screen)
        
        curr_pos = pygame.mouse.get_pos()
        is_clicking = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    debug_mode = not debug_mode
        
        # UPDATE with BRUSH
        word_goal.update(curr_pos, is_clicking)
        word_goal.draw(screen)
        
        # DIBUJAR BRUSH CURSOR
        pygame.draw.circle(screen, (255, 255, 255), curr_pos, BRUSH_RADIUS, 2)
        if is_clicking:
            # Relleno suave al hacer click
            s = pygame.Surface((BRUSH_RADIUS*2, BRUSH_RADIUS*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, 50), (BRUSH_RADIUS, BRUSH_RADIUS), BRUSH_RADIUS)
            screen.blit(s, (curr_pos[0]-BRUSH_RADIUS, curr_pos[1]-BRUSH_RADIUS))
        
        # Mostrar puntos de muestreo del brush (opcional, para ver la "magia")
        if debug_mode:
            for i in range(BRUSH_SAMPLES):
                angle = (2 * math.pi * i) / BRUSH_SAMPLES
                px = curr_pos[0] + math.cos(angle) * BRUSH_RADIUS
                py = curr_pos[1] + math.sin(angle) * BRUSH_RADIUS
                pygame.draw.circle(screen, (0, 255, 255), (int(px), int(py)), 2)

        if debug_mode:
            closest = get_closest_pixel(word_goal, curr_pos)
            if closest:
                # Trace segment from center to center (just for visualization)
                trace = closest.get_debug_trace(curr_pos, curr_pos)
                draw_debug_trace(screen, trace)
                
                # Highlight closest pixel
                pygame.draw.polygon(screen, (255, 0, 255), closest.vertices, 2)
>>>>>>> 5e108aa69be2ff7dba8bd92ebffa13cd1a68be79

           
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    menu.width, menu.height = WIDTH, HEIGHT
                    menu.input_box.center = (WIDTH//2, HEIGHT//2)
                    if game_state == "MENU": menu = GameMenu(WIDTH, HEIGHT)

                if game_state == "MENU":
                    result = menu.handle_event(event)
                    if result == 'EXIT': pygame.quit(); sys.exit()
                    if result:
                        input_word, input_time = result
                        word_goal = WordGoal(input_word, start_y=HEIGHT//2 - 50, screen_width=WIDTH, scale=80)
                        
                        game_state = "PLAYING"
                        camera_x = 0; total_samples = 0; valid_samples = 0
                        final_precision = 100.0; show_results = False
                        time_limit = input_time
                        
                        start_ticks = pygame.time.get_ticks()
                        # --- ACTIVAR PROTECCIÓN DE TIEMPO ---
                        game_start_timestamp = pygame.time.get_ticks()

                elif game_state in ["PLAYING", "FINISHED", "TIME_OVER"]:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB: debug_mode = not debug_mode
                        if event.key == pygame.K_ESCAPE:
                            game_state = "MENU"; menu.reset()

          
            if game_state == "MENU":
                menu.draw(screen)
            
            elif game_state == "PLAYING":
               
                current_time = pygame.time.get_ticks()
                is_protected = (current_time - game_start_timestamp) < 500

                keys = pygame.key.get_pressed()
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: camera_x += camera_speed
                if keys[pygame.K_LEFT] or keys[pygame.K_a]: camera_x -= camera_speed
                camera_x = max(0, min(camera_x, max(0, word_goal.total_width - WIDTH)))

                screen.fill((30, 30, 30))
                draw_grid(screen, WIDTH, HEIGHT, camera_x)
                
                active_click = is_clicking and not is_protected
                
                word_goal.update(last_pos_world, curr_pos_world, active_click, CLICK_SOUND)
                word_goal.draw(screen, camera_x)
                draw_scrollbar(screen, camera_x, word_goal.total_width, WIDTH, HEIGHT)

                elapsed_seconds = (current_time - start_ticks) / 1000
                display_time = 0.0
                
                if time_limit is not None:
                    remaining_time = max(0, time_limit - elapsed_seconds)
                    display_time = remaining_time
                    timer_color = (0, 255, 0) if remaining_time > 10 else (255, 50, 50)
                    if remaining_time <= 0: game_state = "TIME_OVER"; show_results = True
                else:
                    display_time = elapsed_seconds
                    timer_color = (100, 200, 255)

                if active_click: 
                    total_samples += 1
                    if word_goal.is_inside_valid_area(curr_pos_world): valid_samples += 1
                
                current_acc = (valid_samples / total_samples * 100) if total_samples > 0 else 100
                final_precision = current_acc 

                # UI 
                bar_height = 70
                pygame.draw.rect(screen, (25, 25, 35), (0, 0, WIDTH, bar_height))
                pygame.draw.line(screen, (100, 100, 120), (0, bar_height), (WIDTH, bar_height), 2)
                
                progress_pct = word_goal.get_progress()
                y_center = bar_height // 2
                
                # Progreso
                col_prog = (255, 255, 255) if progress_pct < 100 else (0, 255, 100)
                lbl_p = FONT_LABEL.render("PROGRESO:", True, (150, 150, 150))
                val_p = FONT_VALUE.render(f"{int(progress_pct)}%", True, col_prog)
                screen.blit(lbl_p, (30, y_center - 10)); screen.blit(val_p, (160, y_center - 12))

                # Precisión
                col_acc = (100, 255, 100) if current_acc > 80 else ((255, 255, 0) if current_acc > 50 else (255, 50, 50))
                lbl_a = FONT_LABEL.render("PRECISIÓN:", True, (150, 150, 150))
                val_a = FONT_VALUE.render(f"{current_acc:.1f}%", True, col_acc)
                screen.blit(lbl_a, (300, y_center - 10)); screen.blit(val_a, (440, y_center - 12))

                # Tiempo
                lbl_t_txt = "TIEMPO:" if time_limit is None else "RESTANTE:"
                lbl_t = FONT_LABEL.render(lbl_t_txt, True, (150, 150, 150))
                val_t = FONT_VALUE.render(f"{display_time:.1f}s", True, timer_color)
                screen.blit(val_t, (WIDTH - 140, y_center - 12)); screen.blit(lbl_t, (WIDTH - 270, y_center - 10))

                # Rastro visual (Dibuja siempre si haces click)
                if is_clicking:
                    pygame.draw.line(screen, (255, 0, 0), last_pos_screen, curr_pos_screen, 4)

                # Si está protegido, mostrar aviso
                if is_protected:
                    hint = FONT_VALUE.render("¡LISTOS...!", True, (255, 255, 0))
                    screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))

                if word_goal.is_completed() and not show_results:
                    final_precision = current_acc
                    final_time = elapsed_seconds
                    game_state = "FINISHED"
                    show_results = True

                if debug_mode and word_goal:
                    closest = get_closest_pixel(word_goal, curr_pos_world)
                    if closest:
                        screen_verts = [(v[0] - camera_x, v[1]) for v in closest.vertices]
                        if len(screen_verts) > 2: pygame.draw.polygon(screen, (255, 0, 255), screen_verts, 2)
                        p1, p2 = last_pos_world, curr_pos_world
                        if p1 == p2: p2 = (p1[0]+0.1, p1[1]+0.1)
                        trace = closest.get_debug_trace(p1, p2)
                        draw_debug_trace(screen, trace, FONT_VALUE)
                
                txt = FONT_INFO.render("SALIR: ESC | DEBUG: TAB", True, (80, 80, 80))
                screen.blit(txt, (20, HEIGHT - 30))

            elif game_state == "FINISHED":
                screen.fill((30, 30, 30))
                draw_grid(screen, WIDTH, HEIGHT, camera_x)
                word_goal.draw(screen, camera_x)
                s = pygame.Surface((WIDTH, HEIGHT)); s.set_alpha(200); s.fill((0,0,0))
                screen.blit(s, (0,0))
                
                txt_1 = FONT_BIG.render("¡EJERCICIO COMPLETADO!", True, (0, 255, 0))
                txt_2 = FONT_BIG.render(f"Precisión Final: {final_precision:.1f}%", True, (255, 255, 255))
                
                y_off = 0
                if time_limit is None:
                    txt_time = FONT_BIG.render(f"Tiempo Total: {final_time:.2f}s", True, (100, 200, 255))
                    screen.blit(txt_time, txt_time.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
                    y_off = 80

                txt_3 = FONT_INFO.render("Presiona ESC para volver al menú", True, (150, 150, 150))
                screen.blit(txt_1, txt_1.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
                screen.blit(txt_2, txt_2.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
                screen.blit(txt_3, txt_3.get_rect(center=(WIDTH//2, HEIGHT//2 + 100 + y_off)))

            elif game_state == "TIME_OVER":
                screen.fill((50, 10, 10))
                txt_1 = FONT_BIG.render("¡TIEMPO AGOTADO!", True, (255, 100, 100))
                txt_2 = FONT_BIG.render(f"Progreso: {int(word_goal.get_progress())}%", True, (255, 255, 255))
                txt_acc = FONT_BIG.render(f"Precisión: {final_precision:.1f}%", True, (200, 200, 100))
                txt_3 = FONT_INFO.render("Presiona ESC para volver al menú", True, (200, 200, 200))
                
                screen.blit(txt_1, txt_1.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))
                screen.blit(txt_2, txt_2.get_rect(center=(WIDTH//2, HEIGHT//2)))
                screen.blit(txt_acc, txt_acc.get_rect(center=(WIDTH//2, HEIGHT//2 + 70)))
                screen.blit(txt_3, txt_3.get_rect(center=(WIDTH//2, HEIGHT - 100)))

            last_pos_screen = curr_pos_screen
            last_pos_world = curr_pos_world
            pygame.display.flip()
<<<<<<< HEAD

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback; traceback.print_exc()
            game_state = "MENU"
=======
            pygame.time.delay(500) # Pausa breve
            current_word_index += 1
            word_goal = load_level(current_word_index)

        # UI Info
        level_text = FONT.render(f"Nivel: {current_word_index + 1}/{len(words)}", True, (200, 200, 200))
        screen.blit(level_text, (20, 20))
        
        mode_text = FONT.render(f"Modo Brocha: {BRUSH_SAMPLES} puntos/frame", True, (100, 255, 100))
        screen.blit(mode_text, (20, 60))
        
        debug_hint = pygame.font.SysFont('Arial', 16).render("Presiona 'D' para ver Debug DK", True, (100, 100, 100))
        screen.blit(debug_hint, (20, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)
>>>>>>> 5e108aa69be2ff7dba8bd92ebffa13cd1a68be79

if __name__ == "__main__":
    main()