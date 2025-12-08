import pygame
import time

class MenuButton:
    def __init__(self, x, y, w, h, text, color, hover_color, action_value, font_size=28):
        self.original_rect = pygame.Rect(x, y, w, h)
        self.rect = self.original_rect.copy()
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action_value = action_value 
        self.font = pygame.font.SysFont('Arial', font_size, bold=True)
        self.is_hovered = False

    def update(self, mouse_pos):
        if self.original_rect.collidepoint(mouse_pos):
            self.is_hovered = True
            # Efecto de ensanchar suave
            self.rect = self.original_rect.inflate(20, 10) 
        else:
            self.is_hovered = False
            self.rect = self.original_rect.copy()

    def draw(self, surface):
        col = self.hover_color if self.is_hovered else self.color
        # Sombra
        pygame.draw.rect(surface, (20, 20, 20), self.rect.move(4, 4), border_radius=10)
        # Botón
        pygame.draw.rect(surface, col, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)
        
        txt_surf = self.font.render(self.text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, event):
        if self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return True
        return False

class GameMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.title_font = pygame.font.SysFont('Arial', 70, bold=True)
        self.font = pygame.font.Font(None, 50)
        
        self.state = 'MAIN_TITLE' 
        self.selected_mode = None 
        self.selected_time = None 

        # --- BOTONES DEL PRE-MENÚ (Título) ---
        cx, cy = width // 2, height // 2
        self.btn_play = MenuButton(cx - 150, cy, 300, 80, "JUGAR", (0, 180, 0), (50, 230, 50), 'PLAY')
        self.btn_quit = MenuButton(cx - 150, cy + 100, 300, 80, "SALIR", (180, 0, 0), (230, 50, 50), 'QUIT')

        # --- BOTONES DE MODO ---
        btn_w = 300 # Ancho suficiente para "CONTRARRELOJ"
        btn_h = 80
        spacing = 30 
        
        # Posición central para modos
        start_y_mode = (height // 2) - btn_h - (spacing // 2) + 50 
        center_x = (width // 2) - (btn_w // 2)

        self.btn_classic = MenuButton(center_x, start_y_mode, btn_w, btn_h, "CLÁSICO", (0, 100, 200), (0, 150, 255), 'CLASICO')
        self.btn_timer = MenuButton(center_x, start_y_mode + btn_h + spacing, btn_w, btn_h, "CONTRARRELOJ", (200, 50, 0), (255, 100, 0), 'CONTRARRELOJ')

        # --- BOTONES DE TIEMPO ---
        cy_time = height // 2 + 50
        self.time_buttons = [
            MenuButton(cx - 220, cy_time, 100, 80, "15s", (80, 80, 80), (120, 120, 120), 15),
            MenuButton(cx - 100, cy_time, 100, 80, "30s", (80, 80, 80), (120, 120, 120), 30),
            MenuButton(cx + 20, cy_time, 100, 80, "1m", (80, 80, 80), (120, 120, 120), 60),
            MenuButton(cx + 140, cy_time, 100, 80, "3m", (80, 80, 80), (120, 120, 120), 180),
        ]

        # --- CAJA DE TEXTO ---
        input_w = 600
        self.input_box = pygame.Rect((width - input_w)//2, height//2 - 20, input_w, 60)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.box_color = self.color_inactive
        self.box_active = False
        
        self.user_text = ''
        self.cursor_pos = 0  
        self.cursor_visible = True 
        self.last_blink_time = time.time()

        # --- BOTONES DE ACCIÓN (EMPEZAR Y VOLVER) ---
        # Definimos posiciones fijas abajo
        
        # Botón Empezar: Debajo de la caja de texto
        start_y = height // 2 + 60
        self.btn_start = MenuButton(width//2 - 100, start_y, 200, 60, "EMPEZAR", (0, 200, 100), (50, 255, 100), 'START')
        
        # Botón Volver: Debajo de Empezar (o debajo de botones de tiempo)
        # Mismo tamaño que Empezar (200x60)
        back_y = start_y + 80 
        self.btn_back = MenuButton(width//2 - 100, back_y, 200, 60, "VOLVER", (100, 50, 50), (150, 80, 80), 'BACK')
        
    def reset(self):
        self.state = 'SELECT_MODE' 
        self.selected_mode = None
        self.selected_time = None
        self.user_text = ''
        self.cursor_pos = 0
        self.box_active = False

    def go_back(self):
        """Lógica de retroceso en cascada"""
        if self.state == 'SELECT_MODE':
            self.state = 'MAIN_TITLE'
        elif self.state == 'INPUT_TEXT':
            self.state = 'SELECT_MODE'
            self.user_text = ''
            self.selected_mode = None
        elif self.state == 'SELECT_TIME':
            self.state = 'INPUT_TEXT'
            self.selected_time = None

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # --- LÓGICA GLOBAL DE BOTÓN VOLVER (Excepto Main Title) ---
        if self.state != 'MAIN_TITLE':
            # Actualizamos y revisamos click en VOLVER
            # (Lo dibujamos en draw, aquí solo lógica)
            self.btn_back.update(mouse_pos)
            if self.btn_back.is_clicked(event):
                self.go_back()
                return None
            
            # ESCAPE también vuelve
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.go_back()
                return None

        # --- 0. ESTADO: PRE-MENÚ (Título) ---
        if self.state == 'MAIN_TITLE':
            self.btn_play.update(mouse_pos)
            self.btn_quit.update(mouse_pos)

            if self.btn_play.is_clicked(event):
                self.state = 'SELECT_MODE'
            elif self.btn_quit.is_clicked(event):
                return 'EXIT' 

        # --- 1. ESTADO: ELEGIR MODO ---
        elif self.state == 'SELECT_MODE':
            self.btn_classic.update(mouse_pos)
            self.btn_timer.update(mouse_pos)
            
            if self.btn_classic.is_clicked(event):
                self.selected_mode = 'CLASICO'
                self.state = 'INPUT_TEXT'
                self.box_active = True
            elif self.btn_timer.is_clicked(event):
                self.selected_mode = 'CONTRARRELOJ'
                self.state = 'INPUT_TEXT'
                self.box_active = True

        # --- 2. ESTADO: ELEGIR TIEMPO ---
        elif self.state == 'SELECT_TIME':
            for btn in self.time_buttons:
                btn.update(mouse_pos)
                if btn.is_clicked(event):
                    self.selected_time = btn.action_value
                    return (self.user_text, self.selected_time)

        # --- 3. ESTADO: ESCRIBIR TEXTO ---
        elif self.state == 'INPUT_TEXT':
            self.btn_start.update(mouse_pos)

            if self.btn_start.is_clicked(event):
                if self.user_text.strip():
                    if self.selected_mode == 'CLASICO': return (self.user_text, None)
                    else: self.state = 'SELECT_TIME'

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.input_box.collidepoint(event.pos):
                    self.box_active = True
                else:
                    self.box_active = False
                self.box_color = self.color_active if self.box_active else self.color_inactive

            if event.type == pygame.KEYDOWN and self.box_active:
                if event.key == pygame.K_RETURN:
                    if self.user_text.strip():
                        if self.selected_mode == 'CLASICO': return (self.user_text, None)
                        else: self.state = 'SELECT_TIME'
                elif event.key == pygame.K_BACKSPACE:
                    if self.cursor_pos > 0:
                        self.user_text = self.user_text[:self.cursor_pos-1] + self.user_text[self.cursor_pos:]
                        self.cursor_pos -= 1
                elif event.key == pygame.K_DELETE:
                    if self.cursor_pos < len(self.user_text):
                        self.user_text = self.user_text[:self.cursor_pos] + self.user_text[self.cursor_pos+1:]
                elif event.key == pygame.K_LEFT:
                    if self.cursor_pos > 0: self.cursor_pos -= 1
                elif event.key == pygame.K_RIGHT:
                    if self.cursor_pos < len(self.user_text): self.cursor_pos += 1
                elif event.key != pygame.K_ESCAPE:
                    if event.unicode.isalpha() or event.unicode == ' ':
                        char = event.unicode.upper()
                        self.user_text = self.user_text[:self.cursor_pos] + char + self.user_text[self.cursor_pos:]
                        self.cursor_pos += 1

        return None

    def draw(self, screen):
        screen.fill((30, 30, 30))
        
        # Título General (Solo en Main)
        if self.state == 'MAIN_TITLE':
            title_surf = self.title_font.render("ConvexGlyph", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(self.width//2, self.height//2 - 100))
            screen.blit(title_surf, title_rect)
            
            self.btn_play.draw(screen)
            self.btn_quit.draw(screen)
        
        else:
            # Título pequeño
            header_font = pygame.font.SysFont('Arial', 40, bold=True)
            title_surf = header_font.render("ConvexGlyph", True, (150, 150, 150))
            screen.blit(title_surf, (self.width//2 - title_surf.get_width()//2, 30))
            
            # --- DIBUJAR CONTENIDO POR ESTADO ---

            if self.state == 'SELECT_MODE':
                sub_surf = self.font.render("Selecciona un modo:", True, (200, 200, 200))
                screen.blit(sub_surf, sub_surf.get_rect(center=(self.width//2, 180)))
                self.btn_classic.draw(screen)
                self.btn_timer.draw(screen)
                
                # Botón Volver (Debajo de los modos)
                # Ajustamos posición dinámica
                self.btn_back.rect.y = self.btn_timer.rect.bottom + 30
                self.btn_back.original_rect.y = self.btn_timer.rect.bottom + 30
                self.btn_back.draw(screen)

            elif self.state == 'INPUT_TEXT':
                col_mode = (100, 255, 100) if self.selected_mode == 'CLASICO' else (255, 150, 50)
                sub_surf = self.font.render(f"Modo: {self.selected_mode}", True, col_mode)
                screen.blit(sub_surf, sub_surf.get_rect(center=(self.width//2, 150)))
                
                inst_surf = self.font.render("ESCRIBE:", True, (200, 200, 200))
                screen.blit(inst_surf, inst_surf.get_rect(center=(self.width//2, self.height//2 - 60)))

                # Caja de texto
                pygame.draw.rect(screen, self.box_color, self.input_box, 2)
                txt_surface = self.font.render(self.user_text, True, (255, 255, 255))
                txt_before = self.user_text[:self.cursor_pos]
                cursor_x_rel = self.font.size(txt_before)[0]
                vis_w = self.input_box.width - 20
                scroll_x = max(0, cursor_x_rel - vis_w)
                
                clip = self.input_box.inflate(-10, -10)
                screen.set_clip(clip)
                dx, dy = self.input_box.x + 10 - scroll_x, self.input_box.y + 15
                screen.blit(txt_surface, (dx, dy))
                
                if self.box_active:
                    curr = time.time()
                    if curr - self.last_blink_time > 0.5:
                        self.cursor_visible = not self.cursor_visible
                        self.last_blink_time = curr
                    if self.cursor_visible:
                        rx = dx + cursor_x_rel
                        pygame.draw.line(screen, (255, 255, 255), (rx, dy), (rx, dy + 30), 2)
                
                screen.set_clip(None)
                
                # Botones (Empezar y Volver uno debajo del otro)
                self.btn_start.draw(screen)
                
                self.btn_back.rect.y = self.btn_start.rect.bottom + 20
                self.btn_back.original_rect.y = self.btn_start.rect.bottom + 20
                self.btn_back.draw(screen)

            elif self.state == 'SELECT_TIME':
                sub_surf = self.font.render("Elige el tiempo límite:", True, (255, 150, 50))
                screen.blit(sub_surf, sub_surf.get_rect(center=(self.width//2, 200)))
                for btn in self.time_buttons:
                    btn.draw(screen)
                
                # Botón Volver (Debajo de los tiempos)
                self.btn_back.rect.y = self.height // 2 + 150
                self.btn_back.original_rect.y = self.height // 2 + 150
                self.btn_back.draw(screen)