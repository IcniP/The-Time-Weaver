from settings import *
from entity import Player
from cervus import Cervus

class Game:
    def __init__(self):
        pygame.init()
        # Set up the game screen with scaling
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
        pygame.display.set_caption('Time Weaver')
        self.clock = pygame.time.Clock()
        self.running = True
        self.map = pygame.image.load('Assets/Bg/1.png').convert_alpha()
        self.map_scaled = pygame.transform.scale(self.map, (WINDOW_WIDTH, WINDOW_HEIGHT))  # Scale map to fixed resolution

        # Groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # Level
        self.level = 1  

        
        self.cervus = None
        if self.level == 5:
            self.cervus = Cervus((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 + 100), self.all_sprites, None)

       
        self.player = Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), self.all_sprites)

        
        if self.cervus:
            self.cervus.player = self.player

        self.game_active = False
        self.paused = False  
        self.volume = 0.5  

        # Buttons
        self.start_button = self.create_button("Start", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
        self.setting_button = self.create_button("Settings", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.exit_button = self.create_button("Exit", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 90))

        # Pause menu buttons
        self.resume_button = self.create_button("Resume", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        self.return_button = self.create_button("Return to Main Menu", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.pause_setting_button = self.create_button("Settings", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.save_button = self.create_button("Save", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))

        # Settings menu buttons
        self.volume_up_button = self.create_button("Volume +", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        self.volume_down_button = self.create_button("Volume -", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.back_button = self.create_button("Back", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))

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
        """Reset the game state."""
        self.all_sprites.empty()
        self.collision_sprites.empty()

        # Add Cervus first (so it is drawn behind the player)
        self.cervus = None
        if self.level == 5:
            self.cervus = Cervus((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 + 100), self.all_sprites, None)

        # Add player after Cervus (so it is drawn on top)
        self.player = Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), self.all_sprites)

        # Pass the player reference to Cervus
        if self.cervus:
            self.cervus.player = self.player

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
            self.screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, WINDOW_HEIGHT // 3 - title_surface.get_height() // 2))
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
                    elif action == "back":
                        return  # Exit the settings menu

            # Draw settings menu
            self.screen.fill('black')
            self.screen.blit(self.volume_up_button["surface"], self.volume_up_button["rect"])
            self.screen.blit(self.volume_down_button["surface"], self.volume_down_button["rect"])
            self.screen.blit(self.back_button["surface"], self.back_button["rect"])

            pygame.display.update()

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