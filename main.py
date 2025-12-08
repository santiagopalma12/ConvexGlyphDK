import pygame
import sys
# Asegúrate de tener interfaz.py y la carpeta src correctamente
from interfaz import GameMenu  
from src.letter_mesh import generate_polygon_mesh
from src.dk_hierarchy import polyhedron_from_convex_polygon, DKHierarchy

# --- CONFIGURACIÓN INICIAL ---
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("ConvexGlyph - DK Intersection MVP")
clock = pygame.time.Clock()

# --- FUENTES ---
FONT_LABEL = pygame.font.SysFont('Consolas', 24, bold=True)
if not FONT_LABEL: FONT_LABEL = pygame.font.SysFont('Courier New', 24, bold=True)
FONT_VALUE = pygame.font.SysFont('Arial', 30, bold=True)
FONT_BIG = pygame.font.SysFont('Arial', 60, bold=True)
FONT_INFO = pygame.font.SysFont('Arial', 20)

try:
    CLICK_SOUND = pygame.mixer.Sound('assets/click.wav')
except:
    CLICK_SOUND = None

# --- UTILIDADES ---
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

def draw_debug_trace(surface, trace):
    if not trace: return
    PANEL_W = 350
    PANEL_X = surface.get_width() - PANEL_W
    s = pygame.Surface((PANEL_W, surface.get_height()))
    s.set_alpha(230)
    s.fill((20, 20, 30))
    surface.blit(s, (PANEL_X, 0))
    
    title = FONT_VALUE.render("DK Trace", True, (255, 255, 255))
    surface.blit(title, (PANEL_X + 20, 20))
    
    y_offset = 60
    font_dbg = pygame.font.SysFont('Consolas', 12)
    
    for i, (level_idx, polygon, hit) in enumerate(trace):
        if y_offset > surface.get_height() - 50: break
        step_height = 90
        rect = pygame.Rect(PANEL_X + 20, y_offset, PANEL_W - 40, step_height)
        pygame.draw.rect(surface, (40, 40, 50), rect, border_radius=5)
        
        status_color = (100, 255, 100) if hit else (255, 100, 100)
        pygame.draw.rect(surface, status_color, rect, 2, border_radius=5)
        
        surface.blit(font_dbg.render(f"Nivel: {level_idx}", True, (200,200,200)), (rect.x + 10, rect.y + 10))
        surface.blit(font_dbg.render(f"Result: {'HIT' if hit else 'MISS'}", True, status_color), (rect.x + 10, rect.y + 50))
        y_offset += step_height + 10

# --- CLASES DEL JUEGO ---

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
        
    def update(self, last_pos, curr_pos, is_clicking):
        hit_any = False
        for pixel in self.pixels:
            if pixel.update(last_pos, curr_pos, is_clicking):
                hit_any = True
        if hit_any and CLICK_SOUND:
            CLICK_SOUND.play()

    def is_completed(self):
        return all(pixel.completed for pixel in self.pixels)

    def draw(self, surface, camera_x):
        for pixel in self.pixels:
            screen_vertices = [(v[0] - camera_x, v[1]) for v in pixel.vertices]
            # Optimización (Culling)
            if any(-50 < v[0] < surface.get_width() + 50 for v in screen_vertices):
                color = (0, 255, 0) if pixel.completed else ((255, 255, 0) if pixel.highlight else (100, 100, 255))
                pygame.draw.polygon(surface, color, screen_vertices, 0)
                pygame.draw.polygon(surface, (50, 50, 50), screen_vertices, 1)

class WordGoal:
    def __init__(self, word, start_y, screen_width, scale=50):
        self.polygons = []
        
        # Calcular ancho total
        letter_spacing = scale * 1.5 
        word_spacing = scale * 1.0
        
        calculated_width = 0
        for char in word:
            if char == ' ':
                calculated_width += word_spacing
            else:
                calculated_width += letter_spacing
        
        # Calcular posición inicial (Centrado)
        if calculated_width < screen_width:
            start_x = (screen_width - calculated_width) // 2
        else:
            start_x = 50

        # Crear letras
        current_x = start_x
        for char in word:
            if char == ' ':
                current_x += word_spacing
            else:
                self.polygons.append(LetterGoal(char, current_x, start_y, scale))
                current_x += letter_spacing
            
        self.total_width = max(calculated_width + 100, screen_width)

    def update(self, last_pos, curr_pos, is_clicking):
        for poly in self.polygons:
            poly.update(last_pos, curr_pos, is_clicking)

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
        for poly in self.polygons:
            poly.draw(surface, camera_x)

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

# --- MAIN LOOP ---
def main():
    global WIDTH, HEIGHT, screen
    menu = GameMenu(WIDTH, HEIGHT)
    game_state = "MENU"
    word_goal = None
    
    camera_x = 0
    camera_speed = 15
    last_pos_screen = pygame.mouse.get_pos()
    last_pos_world = (last_pos_screen[0], last_pos_screen[1])
    
    debug_mode = False

    # Variables de estado
    time_limit = None
    start_ticks = 0
    total_samples = 0
    valid_samples = 0
    final_precision = 0
    final_time = 0.0
    show_results = False

    while True:
        try:
            dt = clock.tick(60)
            curr_pos_screen = pygame.mouse.get_pos()
            is_clicking = pygame.mouse.get_pressed()[0]
            curr_pos_world = (curr_pos_screen[0] + camera_x, curr_pos_screen[1])

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
                    
                    if result == 'EXIT':
                        pygame.quit()
                        sys.exit()

                    if result:
                        input_word, input_time = result
                        word_goal = WordGoal(input_word, start_y=HEIGHT//2 - 50, screen_width=WIDTH, scale=80)
                        
                        game_state = "PLAYING"
                        camera_x = 0
                        total_samples = 0
                        valid_samples = 0
                        final_precision = 100.0
                        show_results = False
                        
                        time_limit = input_time
                        start_ticks = pygame.time.get_ticks()

                elif game_state in ["PLAYING", "FINISHED", "TIME_OVER"]:
                    if event.type == pygame.KEYDOWN:
                        # --- MODIFICADO: Debug con TAB ---
                        if event.key == pygame.K_TAB: 
                            debug_mode = not debug_mode
                        
                        if event.key == pygame.K_ESCAPE:
                            game_state = "MENU"
                            menu.reset()

            # --- DIBUJADO Y LÓGICA ---
            if game_state == "MENU":
                menu.draw(screen)
            
            elif game_state == "PLAYING":
                keys = pygame.key.get_pressed()
                # --- MODIFICADO: Cámara con Flechas y WASD (A/D) ---
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: camera_x += camera_speed
                if keys[pygame.K_LEFT] or keys[pygame.K_a]: camera_x -= camera_speed
                
                max_cam = max(0, word_goal.total_width - WIDTH)
                camera_x = max(0, min(camera_x, max_cam))

                screen.fill((30, 30, 30))
                draw_grid(screen, WIDTH, HEIGHT, camera_x)
                
                word_goal.update(last_pos_world, curr_pos_world, is_clicking)
                word_goal.draw(screen, camera_x)
                draw_scrollbar(screen, camera_x, word_goal.total_width, WIDTH, HEIGHT)

                # Tiempo
                elapsed_seconds = (pygame.time.get_ticks() - start_ticks) / 1000
                display_time = 0.0
                
                if time_limit is not None:
                    remaining_time = max(0, time_limit - elapsed_seconds)
                    display_time = remaining_time
                    timer_color = (0, 255, 0) if remaining_time > 10 else (255, 50, 50)
                    
                    if remaining_time <= 0:
                        game_state = "TIME_OVER"
                        show_results = True
                else:
                    display_time = elapsed_seconds
                    timer_color = (100, 200, 255)

                # Precisión Logic
                if is_clicking:
                    total_samples += 1
                    if word_goal.is_inside_valid_area(curr_pos_world):
                        valid_samples += 1
                
                current_acc = (valid_samples / total_samples * 100) if total_samples > 0 else 100
                final_precision = current_acc 

                # --- UI DE ESTADO ---
                bar_height = 70
                pygame.draw.rect(screen, (25, 25, 35), (0, 0, WIDTH, bar_height))
                pygame.draw.line(screen, (100, 100, 120), (0, bar_height), (WIDTH, bar_height), 2)
                
                progress_pct = word_goal.get_progress()
                y_center = bar_height // 2
                
                col_prog = (255, 255, 255) if progress_pct < 100 else (0, 255, 100)
                col_acc = (100, 255, 100) if current_acc > 80 else ((255, 255, 0) if current_acc > 50 else (255, 50, 50))

                lbl_prog = FONT_LABEL.render("PROGRESO:", True, (150, 150, 150))
                val_prog = FONT_VALUE.render(f"{int(progress_pct)}%", True, col_prog)
                r_lbl_p = lbl_prog.get_rect(midleft=(30, y_center))
                r_val_p = val_prog.get_rect(midleft=(r_lbl_p.right + 10, y_center - 2))
                screen.blit(lbl_prog, r_lbl_p); screen.blit(val_prog, r_val_p)

                start_x_acc = r_val_p.right + 60
                lbl_acc = FONT_LABEL.render("PRECISIÓN:", True, (150, 150, 150))
                val_acc = FONT_VALUE.render(f"{current_acc:.1f}%", True, col_acc)
                r_lbl_a = lbl_acc.get_rect(midleft=(start_x_acc, y_center))
                r_val_a = val_acc.get_rect(midleft=(r_lbl_a.right + 10, y_center - 2))
                screen.blit(lbl_acc, r_lbl_a); screen.blit(val_acc, r_val_a)

                # DIBUJAR TIEMPO
                lbl_text = "TIEMPO:" if time_limit is None else "RESTANTE:"
                lbl_time = FONT_LABEL.render(lbl_text, True, (150, 150, 150))
                val_time_surf = FONT_VALUE.render(f"{display_time:.1f}s", True, timer_color)
                
                r_val_t = val_time_surf.get_rect(midright=(WIDTH - 30, y_center - 2))
                r_lbl_t = lbl_time.get_rect(midright=(r_val_t.left - 10, y_center))
                screen.blit(val_time_surf, r_val_t); screen.blit(lbl_time, r_lbl_t)

                if is_clicking:
                    pygame.draw.line(screen, (255, 0, 0), last_pos_screen, curr_pos_screen, 4)

                # Verificar fin
                if word_goal.is_completed() and not show_results:
                    final_precision = current_acc
                    final_time = elapsed_seconds
                    game_state = "FINISHED"
                    show_results = True

                if debug_mode and word_goal:
                    closest = get_closest_pixel(word_goal, curr_pos_world)
                    if closest:
                        screen_verts = [(v[0] - camera_x, v[1]) for v in closest.vertices]
                        if len(screen_verts) > 2:
                             pygame.draw.polygon(screen, (255, 0, 255), screen_verts, 2)
                        p1, p2 = last_pos_world, curr_pos_world
                        if p1 == p2: p2 = (p1[0]+0.1, p1[1]+0.1)
                        trace = closest.get_debug_trace(p1, p2)
                        draw_debug_trace(screen, trace)
                
                # --- MODIFICADO: Texto inferior ---
                txt = FONT_INFO.render("SALIR: ESC | DEBUG: TAB", True, (80, 80, 80))
                screen.blit(txt, (20, HEIGHT - 30))

            # --- PANTALLA: COMPLETADO ---
            elif game_state == "FINISHED":
                screen.fill((30, 30, 30))
                draw_grid(screen, WIDTH, HEIGHT, camera_x)
                word_goal.draw(screen, camera_x)
                s = pygame.Surface((WIDTH, HEIGHT)); s.set_alpha(200); s.fill((0,0,0))
                screen.blit(s, (0,0))
                
                txt_1 = FONT_BIG.render("¡EJERCICIO COMPLETADO!", True, (0, 255, 0))
                txt_2 = FONT_BIG.render(f"Precisión Final: {final_precision:.1f}%", True, (255, 255, 255))
                
                if time_limit is None:
                    txt_time = FONT_BIG.render(f"Tiempo Total: {final_time:.2f}s", True, (100, 200, 255))
                    screen.blit(txt_time, txt_time.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
                    y_inst = HEIGHT//2 + 150
                else:
                    y_inst = HEIGHT//2 + 100

                txt_3 = FONT_INFO.render("Presiona ESC para volver al menú", True, (150, 150, 150))
                
                screen.blit(txt_1, txt_1.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
                screen.blit(txt_2, txt_2.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
                screen.blit(txt_3, txt_3.get_rect(center=(WIDTH//2, y_inst)))

            # --- PANTALLA: TIEMPO AGOTADO ---
            elif game_state == "TIME_OVER":
                screen.fill((50, 10, 10))
                txt_1 = FONT_BIG.render("¡TIEMPO AGOTADO!", True, (255, 100, 100))
                txt_2 = FONT_BIG.render(f"Progreso: {int(word_goal.get_progress())}%", True, (255, 255, 255))
                txt_acc_fail = FONT_BIG.render(f"Precisión: {final_precision:.1f}%", True, (200, 200, 100))
                txt_3 = FONT_INFO.render("Presiona ESC para volver al menú", True, (200, 200, 200))
                
                screen.blit(txt_1, txt_1.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))
                screen.blit(txt_2, txt_2.get_rect(center=(WIDTH//2, HEIGHT//2)))
                screen.blit(txt_acc_fail, txt_acc_fail.get_rect(center=(WIDTH//2, HEIGHT//2 + 70)))
                screen.blit(txt_3, txt_3.get_rect(center=(WIDTH//2, HEIGHT - 100)))

            last_pos_screen = curr_pos_screen
            last_pos_world = curr_pos_world
            pygame.display.flip()

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback; traceback.print_exc()
            game_state = "MENU"
            if 'menu' in locals(): menu.reset()

if __name__ == "__main__":
    main()