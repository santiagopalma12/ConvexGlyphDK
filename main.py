import pygame
import sys

from src.menu import GameMenu  
from src.game_entities import WordGoal, get_closest_pixel
from src.utils_draw import draw_grid, draw_scrollbar, draw_debug_trace

pygame.init()
pygame.mixer.init()

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

try:
    CLICK_SOUND = pygame.mixer.Sound('assets/click.wav')
except:
    CLICK_SOUND = None

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
    
    time_limit = None
    start_ticks = 0
    total_samples = 0
    valid_samples = 0
    final_precision = 0
    final_time = 0.0
    show_results = False

    game_start_timestamp = 0 

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

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback; traceback.print_exc()
            game_state = "MENU"

if __name__ == "__main__":
    main()