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

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update
            self.all_sprites.update(dt)

            # draw 
            self.screen.fill(BG_COLOR)
            self.all_sprites.draw(self.screen)
            pygame.display.update()
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
