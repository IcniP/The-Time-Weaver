from settings import *
from entity import Player

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Time Weaver')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups 
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # add player
        self.player = Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), self.all_sprites)

        self.game_active = False
        
    def main_menu(self):
        #font for title, size 100
        title_font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 100)
        title_surface = title_font.render('The Time Weaver', True, 'White')

        #font for space to start, size 50
        start_font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 50)
        presstostart_surface = start_font.render('Press Space to Start', True, 'White')
        
        while not self.game_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game_active = True

            # draw title screen
            self.screen.fill('black')
            self.screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, WINDOW_HEIGHT // 2 - title_surface.get_height() // 2))
            self.screen.blit(presstostart_surface, (WINDOW_WIDTH // 2 - presstostart_surface.get_width() // 2, WINDOW_HEIGHT // 2 + title_surface.get_height() // 2))
            pygame.display.update()

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.game_active:
                # update
                self.all_sprites.update(dt)

                # draw 
                self.screen.fill(BG_COLOR)
                self.all_sprites.draw(self.screen)
                pygame.display.update()
            else:
                self.main_menu()
                

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()