from settings import *
from entity import *
from cervus import Cervus
import xml.etree.ElementTree as ET
from pathlib import Path
from mainmenu import MainMenuManager
from noliictu import Noliictu

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
        pygame.display.set_caption('Time Weaver')
        self.clock = pygame.time.Clock()
        self.running = True

        self.map = pygame.image.load('Assets/Bg/1.png').convert_alpha()
        self.map_scaled = pygame.transform.scale(self.map, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.level = 4
        self.mapz = {
            1: "lvl1.tmx",
            2: "lvl2.tmx",
            3: "lvl3.tmx",
            4: "lvl4.tmx",
            5: "lvl5.tmx"
        }.get(self.level, "test.tmx")

        self.player = Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), self.all_sprites, self.collision_sprites)
        self.fix_tmx_tileset('data/maps', 'Assets/Tilesets')
        self.game_active = False
        self.paused = False

        self.menu_manager = MainMenuManager(self.screen, self)

    def fix_tmx_tileset(self, map_folder, tileset_folder):
        map_folder = Path(map_folder)
        tileset_folder = Path(tileset_folder)
        for tmx_file in map_folder.glob('*.tmx'):
            tree = ET.parse(tmx_file)
            root = tree.getroot()
            for tileset in root.findall('tileset'):
                image = tileset.find('image')
                if image is not None:
                    filename = Path(image.attrib['source']).name
                    correct_path = tileset_folder / filename
                    image.attrib['source'] = str(correct_path.as_posix())
            tree.write(tmx_file, encoding='utf-8', xml_declaration=True)

    def reset_game(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.map1()

    def map1(self):
        map = load_pygame(join('data', 'maps', self.mapz))
        for x, y, image in map.get_layer_by_name('ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for collision in map.get_layer_by_name('pits'):
            CollisionSprite((collision.x, collision.y), pygame.Surface((collision.width, collision.height)), self.collision_sprites)

        # --- sementara player kosong ---
        player_pos = None

        for marker in map.get_layer_by_name('entities'):
            if marker.name == 'Player':
                player_pos = (marker.x, marker.y)

        # Setelah semua marker dicek, baru spawn player
        if player_pos:
            self.player = Player(player_pos, self.all_sprites, self.collision_sprites)

        # Setelah player ada, baru spawn musuh
        for marker in map.get_layer_by_name('entities'):
            if marker.name == 'sword':
                Humanoid('Sword', (marker.x, marker.y), self.all_sprites, self.collision_sprites)
            elif marker.name == 'axe':
                Humanoid('Axe', (marker.x, marker.y), self.all_sprites, self.collision_sprites)
            elif marker.name == 'spear':
                Humanoid('Spear', (marker.x, marker.y), self.all_sprites, self.collision_sprites)
            elif marker.name == 'Cervus':
                self.cervus = Cervus((marker.x, marker.y), self.all_sprites, self.player)
            elif marker.name == 'Noliictu':
                self.noliictu = Noliictu((marker.x, marker.y), self.all_sprites, self.player)

    def run(self):
        while self.running:
            if not self.paused:
                dt = self.clock.tick(FRAMERATE) / 1000
            else:
                self.clock.tick(FRAMERATE)
                dt = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.game_active:
                        self.menu_manager.pause_menu()

            if self.game_active:
                if not self.paused:
                    self.all_sprites.update(dt)

                self.screen.blit(self.map_scaled, (0, 0))
                self.all_sprites.draw(self.player.rect.center)
                pygame.display.update()
            else:
                self.menu_manager.main_menu()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()