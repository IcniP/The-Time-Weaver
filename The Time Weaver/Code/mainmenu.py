import pygame
from settings import *

class MainMenuManager:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game  # reference ke Game instance
        self.volume = 0.5

        self.start_button = self.create_button("Start", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
        self.setting_button = self.create_button("Settings", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.exit_button = self.create_button("Exit", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 90))

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

    def main_menu(self):
        title_font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 100)
        title_surface = title_font.render('The Time Weaver', True, 'White')

        while not self.game.game_active and self.game.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = self.detect_mouse_collision(mouse_pos, {
                        "start": self.start_button,
                        "settings": self.setting_button,
                        "exit": self.exit_button
                    })
                    if action == "start":
                        self.game.reset_game()
                        self.game.game_active = True
                    elif action == "settings":
                        self.settings_menu()
                    elif action == "exit":
                        self.game.running = False

            self.screen.fill('black')
            self.screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, WINDOW_HEIGHT // 3 - title_surface.get_height() // 2))
            self.screen.blit(self.start_button["surface"], self.start_button["rect"])
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
                    elif action == "settings":
                        self.settings_menu()
                    elif action == "save":
                        print("Game saved!")  # Placeholder

            self.screen.fill('black')
            self.screen.blit(self.resume_button["surface"], self.resume_button["rect"])
            self.screen.blit(self.return_button["surface"], self.return_button["rect"])
            self.screen.blit(self.pause_setting_button["surface"], self.pause_setting_button["rect"])
            self.screen.blit(self.save_button["surface"], self.save_button["rect"])

            pygame.display.update()
            self.game.clock.tick(FRAMERATE)  # <-- Add this line

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
                        pygame.mixer.music.set_volume(self.volume)
                    elif action == "volume_down":
                        self.volume = max(0.0, self.volume - 0.1)
                        pygame.mixer.music.set_volume(self.volume)
                    elif action == "back":
                        return

            self.screen.fill('black')
            self.screen.blit(self.volume_up_button["surface"], self.volume_up_button["rect"])
            self.screen.blit(self.volume_down_button["surface"], self.volume_down_button["rect"])
            self.screen.blit(self.back_button["surface"], self.back_button["rect"])

            pygame.display.update()
