from settings import *
from entity import Player

class Game:
    def __init__(self):
        pygame.init()
        self.current_resolution = "normal"  # Default resolution
        self.screen = pygame.display.set_mode(RESOLUTIONS[self.current_resolution])
        pygame.display.set_caption('Time Weaver')
        self.clock = pygame.time.Clock()
        self.running = True
        self.map = pygame.image.load('Assets/Bg/1.png').convert_alpha()
        self.map_scaled = self.map  # Scaled version of the map

        # groups 
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # add player
        self.player = Player((RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2), self.all_sprites)

        self.game_active = False
        self.paused = False  # New variable to track if the game is paused
        self.volume = 0.5  # Default volume (50%)

        # Buttons
        self.start_button = self.create_button("Start", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 + 30))
        self.setting_button = self.create_button("Settings", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 + 60))
        self.exit_button = self.create_button("Exit", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 + 90))

        # Pause menu buttons
        self.resume_button = self.create_button("Resume", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 - 60))
        self.return_button = self.create_button("Return to Main Menu", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 - 30))
        self.pause_setting_button = self.create_button("Settings", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2))
        self.save_button = self.create_button("Save", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 + 30))

        # Settings menu buttons
        self.volume_up_button = self.create_button("Volume +", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 - 60))
        self.volume_down_button = self.create_button("Volume -", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 - 30))
        self.size_normal_button = self.create_button("Window 1x", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2))
        self.size_2x_button = self.create_button("Window 2x", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 + 30))
        self.size_3x_button = self.create_button("Window 3x", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 + 60))
        self.back_button = self.create_button("Back", (RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2 + 90))

    def create_button(self, text, position):
        """Create a button with text and position."""
        font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 40)
        surface = font.render(text, True, 'White')
        rect = surface.get_rect(center=position)
        return {"surface": surface, "rect": rect}

    def detect_mouse_collision(self, mouse_pos, buttons):
        """Detect if the mouse is colliding with any button."""
        for button_name, button in buttons.items():
            if button["rect"].collidepoint(mouse_pos):
                return button_name
        return None

    def reset_game(self):
        self.all_sprites.empty()  
        self.collision_sprites.empty()  
        self.player = Player((RESOLUTIONS[self.current_resolution][0] // 2, RESOLUTIONS[self.current_resolution][1] // 2), self.all_sprites)  

    def main_menu(self):
        """Display the main menu and handle button interactions."""
        title_font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 100)
        title_surface = title_font.render('The Time Weaver', True, 'White')

        while not self.game_active and self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                    action = self.detect_mouse_collision(mouse_pos, {
                        "start": self.start_button,
                        "settings": self.setting_button,
                        "exit": self.exit_button
                    })
                    if action == "start":
                        self.reset_game()  # Reset the game when starting
                        self.game_active = True
                    elif action == "settings":
                        self.settings_menu()
                    elif action == "exit":
                        self.running = False

            # Draw title screen
            self.screen.fill('black')
            self.screen.blit(title_surface, (RESOLUTIONS[self.current_resolution][0] // 2 - title_surface.get_width() // 2, RESOLUTIONS[self.current_resolution][1] // 3 - title_surface.get_height() // 2))
            self.screen.blit(self.start_button["surface"], self.start_button["rect"])
            self.screen.blit(self.setting_button["surface"], self.setting_button["rect"])
            self.screen.blit(self.exit_button["surface"], self.exit_button["rect"])

            pygame.display.update()

    def pause_menu(self):
        """Display the pause menu and handle button interactions."""
        self.paused = True  # Set the game to paused
        while self.paused and self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                    action = self.detect_mouse_collision(mouse_pos, {
                        "resume": self.resume_button,
                        "return": self.return_button,
                        "settings": self.pause_setting_button,
                        "save": self.save_button
                    })
                    if action == "resume":
                        self.paused = False  # Resume the game
                    elif action == "return":
                        self.game_active = False
                        self.paused = False
                    elif action == "settings":
                        self.settings_menu()
                    elif action == "save":
                        print("Game saved!")  # Placeholder for save functionality

            # Draw pause menu
            self.screen.fill('black')
            self.screen.blit(self.resume_button["surface"], self.resume_button["rect"])
            self.screen.blit(self.return_button["surface"], self.return_button["rect"])
            self.screen.blit(self.pause_setting_button["surface"], self.pause_setting_button["rect"])
            self.screen.blit(self.save_button["surface"], self.save_button["rect"])

            pygame.display.update()

    def settings_menu(self):
        """Display the settings menu and handle button interactions."""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                    action = self.detect_mouse_collision(mouse_pos, {
                        "volume_up": self.volume_up_button,
                        "volume_down": self.volume_down_button,
                        "size_normal": self.size_normal_button,
                        "size_2x": self.size_2x_button,
                        "size_3x": self.size_3x_button,
                        "back": self.back_button
                    })
                    if action == "volume_up":
                        self.volume = min(1.0, self.volume + 0.1)  # Increase volume, max 1.0
                        pygame.mixer.music.set_volume(self.volume)
                        print(f"Volume: {self.volume * 100:.0f}%")
                    elif action == "volume_down":
                        self.volume = max(0.0, self.volume - 0.1)  # Decrease volume, min 0.0
                        pygame.mixer.music.set_volume(self.volume)
                        print(f"Volume: {self.volume * 100:.0f}%")
                    elif action == "size_normal":
                        self.set_window_size("normal")
                        print("Window size set to 1x")
                    elif action == "size_2x":
                        self.set_window_size("2x")
                        print("Window size set to 2x")
                    elif action == "size_3x":
                        self.set_window_size("3x")
                        print("Window size set to 3x")
                    elif action == "back":
                        return  # Exit the settings menu

            # Draw settings menu
            self.screen.fill('black')
            self.screen.blit(self.volume_up_button["surface"], self.volume_up_button["rect"])
            self.screen.blit(self.volume_down_button["surface"], self.volume_down_button["rect"])
            self.screen.blit(self.size_normal_button["surface"], self.size_normal_button["rect"])
            self.screen.blit(self.size_2x_button["surface"], self.size_2x_button["rect"])
            self.screen.blit(self.size_3x_button["surface"], self.size_3x_button["rect"])
            self.screen.blit(self.back_button["surface"], self.back_button["rect"])

            pygame.display.update()

    def set_window_size(self, resolution_key):
        """Set the window size and scale all elements."""
        self.current_resolution = resolution_key
        new_width, new_height = RESOLUTIONS[resolution_key]
        self.screen = pygame.display.set_mode((new_width, new_height))

        # Scale the background
        self.map_scaled = pygame.transform.scale(self.map, (new_width, new_height))

        # Recreate buttons with updated positions and sizes
        self.start_button = self.create_button("Start", (new_width // 2, new_height // 2 + 30))
        self.setting_button = self.create_button("Settings", (new_width // 2, new_height // 2 + 60))
        self.exit_button = self.create_button("Exit", (new_width // 2, new_height // 2 + 90))

        self.resume_button = self.create_button("Resume", (new_width // 2, new_height // 2 - 60))
        self.return_button = self.create_button("Return to Main Menu", (new_width // 2, new_height // 2 - 30))
        self.pause_setting_button = self.create_button("Settings", (new_width // 2, new_height // 2))
        self.save_button = self.create_button("Save", (new_width // 2, new_height // 2 + 30))

        self.volume_up_button = self.create_button("Volume +", (new_width // 2, new_height // 2 - 60))
        self.volume_down_button = self.create_button("Volume -", (new_width // 2, new_height // 2 - 30))
        self.size_normal_button = self.create_button("Window 1x", (new_width // 2, new_height // 2))
        self.size_2x_button = self.create_button("Window 2x", (new_width // 2, new_height // 2 + 30))
        self.size_3x_button = self.create_button("Window 3x", (new_width // 2, new_height // 2 + 60))
        self.back_button = self.create_button("Back", (new_width // 2, new_height // 2 + 90))

        # Update player position
        self.player.rect.center = (new_width // 2, new_height // 2)

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.game_active:
                        self.pause_menu()

            if self.game_active and not self.paused:
                # Update
                self.all_sprites.update(dt)

                # Draw the scaled background
                self.screen.blit(self.map_scaled, (0, 0))
                self.all_sprites.draw(self.screen)
                pygame.display.update()
            elif not self.game_active:
                self.main_menu()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()