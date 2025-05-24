from settings import *
from save_system import SaveManager

class MainMenuManager:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game  # reference ke Game instance
        self.volume = 0.2

        self.lvl4_music = pygame.mixer.Sound('Assets/ost/lacrimosatnbe.mp3')
        self.lobby_music = pygame.mixer.Sound('Assets/ost/lobby.mp3')

        self.lobbybg = pygame.image.load('Assets/lobby/1.png').convert_alpha()

        self.start_button = self.create_button("Start", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
        self.load_button = self.create_button("Load", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.setting_button = self.create_button("Settings", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 90))
        self.exit_button = self.create_button("Exit", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120))
        
        self.resume_button = self.create_button("Resume", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        self.return_button = self.create_button("Return to Main Menu", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.pause_setting_button = self.create_button("Settings", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.save_button = self.create_button("Save", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))

        self.volume_up_button = self.create_button("Volume +", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        self.volume_down_button = self.create_button("Volume -", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.back_button = self.create_button("Back", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))

    def create_button(self, text, position):
        font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 40)
        surface = font.render(text, True, 'White')
        rect = surface.get_rect(center=position)
        return {"surface": surface, "rect": rect}

    def detect_mouse_collision(self, mouse_pos, buttons):
        for button_name, button in buttons.items():
            if button["rect"].collidepoint(mouse_pos):
                return button_name
        return None
    
    def load_menu(self):
        pygame.event.clear()
        font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 30)
        back_btn = self.create_button("Back", (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80))

        while self.game.running:
            # refresh
            saves = SaveManager.list_saves()
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # klik slot
                    for idx, (slot, meta) in enumerate(saves):
                        rect = pygame.Rect(WINDOW_WIDTH//2-140, 180+idx*42, 280, 40)
                        if rect.collidepoint(mouse_pos):
                            self.game.load_game_slot(slot)   # → restore & masuk game
                            return

                    # klik back
                    if back_btn["rect"].collidepoint(mouse_pos):
                        return                               # balik ke main_menu()

            # ──── DRAW ──────────────────────────────────────────────────────
            self.screen.fill("black")
            self.screen.blit(font.render("Select Save", True, "white"),
                            (WINDOW_WIDTH//2-90, 120))

            for idx, (slot, meta) in enumerate(saves):
                txt = f"Slot {slot} • LV {meta.get('level', '?')} • {meta['checkpoint']}"
                surf = font.render(txt, True, "white")
                rect = surf.get_rect(center=(WINDOW_WIDTH//2, 200+idx*42))
                self.screen.blit(surf, rect)

            # kalau belum ada save sama sekali
            if not saves:
                note = font.render("No save file found", True, "gray")
                self.screen.blit(note, note.get_rect(center=(WINDOW_WIDTH//2, 240)))

            # back button
            self.screen.blit(back_btn["surface"], back_btn["rect"])

            pygame.display.update()
            self.game.clock.tick(FRAMERATE)

    def flash_text(self, text: str, seconds: float = 2):
        font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 40)
        surf = font.render(text, True, 'white')
        rect = surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        start = pygame.time.get_ticks()
        while (pygame.time.get_ticks() - start) < seconds * 1000 and self.game.running:
            # keep polling quit so ESC saat pop-up tidak freeze
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                    return

            self.screen.blit(surf, rect)
            pygame.display.update()
            self.game.clock.tick(FRAMERATE)

    def main_menu(self):
        title_font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 100)
        title_surface = title_font.render('The Time Weaver', True, 'White')

        # Play lobby music kalau belum aktif
        if not pygame.mixer.get_busy():
            self.lobby_music.play(loops=-1)

        while not self.game.game_active and self.game.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = self.detect_mouse_collision(mouse_pos, {
                        "start": self.start_button,
                        "load": self.load_button,
                        "settings": self.setting_button,
                        "exit": self.exit_button
                    })
                    if action == "start":
                        self.game.reset_game()
                        self.game.game_active = True
                        self.lobby_music.stop()

                        if self.game.level == '4-0':
                            self.lvl4_music.play(loops=-1)
                    elif action == "load":
                        self.load_menu()   
                    elif action == "settings":
                        self.settings_menu()
                    elif action == "exit":
                        self.game.running = False

            self.screen.fill('black')
            self.screen.blit(self.lobbybg, (0, 0))
            self.screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, WINDOW_HEIGHT // 3 - title_surface.get_height() // 2))
            self.screen.blit(self.start_button["surface"], self.start_button["rect"])
            self.screen.blit(self.load_button["surface"], self.load_button["rect"])
            self.screen.blit(self.setting_button["surface"], self.setting_button["rect"])
            self.screen.blit(self.exit_button["surface"], self.exit_button["rect"])

            pygame.display.update()

    def pause_menu(self):
        self.game.paused = True
        while self.game.paused and self.game.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = self.detect_mouse_collision(mouse_pos, {
                        "resume": self.resume_button,
                        "return": self.return_button,
                        "settings": self.pause_setting_button,
                        "save": self.save_button
                    })
                    if action == "resume":
                        self.game.paused = False
                    elif action == "return":
                        self.game.game_active = False
                        self.game.paused = False
                        self.lvl4_music.stop()
                        self.lobby_music.play(loops=-1)
                    elif action == "settings":
                        self.settings_menu()
                    elif action == "save":
                        SaveManager.save_game(self.game.player,
                                            checkpoint=self.game.level,
                                            slot=1)
                        self.flash_text("Game Saved!", 2)

            self.screen.fill('black')
            self.screen.blit(self.resume_button["surface"], self.resume_button["rect"])
            self.screen.blit(self.return_button["surface"], self.return_button["rect"])
            self.screen.blit(self.pause_setting_button["surface"], self.pause_setting_button["rect"])
            self.screen.blit(self.save_button["surface"], self.save_button["rect"])

            pygame.display.update()
            self.game.clock.tick(FRAMERATE)

    def set_all_volume(self, volume):
        self.lvl4_music.set_volume(volume)
        self.lobby_music.set_volume(volume*1.5)

    def settings_menu(self):
        while self.game.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = self.detect_mouse_collision(mouse_pos, {
                        "volume_up": self.volume_up_button,
                        "volume_down": self.volume_down_button,
                        "back": self.back_button
                    })
                    if action == "volume_up":
                        self.volume = min(1.0, self.volume + 0.1)
                        self.set_all_volume(self.volume)
                    elif action == "volume_down":
                        self.volume = max(0.0, self.volume - 0.1)
                        self.set_all_volume(self.volume)
                    elif action == "back":
                        return

            self.screen.fill('black')
            self.screen.blit(self.volume_up_button["surface"], self.volume_up_button["rect"])
            self.screen.blit(self.volume_down_button["surface"], self.volume_down_button["rect"])
            self.screen.blit(self.back_button["surface"], self.back_button["rect"])

            pygame.display.update()

class Transition:
    def __init__(self, duration):
        self.duration = duration
        self.timer = 0
        self.active = False
        self.alpha = 0
        self.next_state = None
    
    def start(self, mode='fade'):
        self.start_time = pygame.time.get_ticks()
        self.active = True
        self.fade_in = (mode == 'fadein')

    def update(self, dt):
        if not self.active:
            return
        
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.duration:
            self.active = False
            return
            

    def draw(self, surface):
        if not self.active:
            return
        elapsed = pygame.time.get_ticks() - self.start_time
        alpha = int((elapsed / self.duration) * 255)
        if self.fade_in:
            alpha = 255 - alpha
        alpha = max(0, min(alpha, 255))

        fade_surf = pygame.Surface(surface.get_size())
        fade_surf.fill((0, 0, 0))
        fade_surf.set_alpha(alpha)
        surface.blit(fade_surf, (0, 0))

        if self.next_state == 'respawn' or (hasattr(self, 'fade_reason') and self.fade_reason == 'respawn'):
            font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 80)
            text = font.render("YOU DIED", True, 'Red')
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            surface.blit(text, rect)