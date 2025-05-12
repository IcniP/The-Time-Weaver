from settings import *
from player import Player
from humanoid import Humanoid
from monstrosity import Monstrosity
from entity import AllSprites, Sprite, CollisionSprite
from interface import *
from cervus import Cervus
import xml.etree.ElementTree as ET
from pathlib import Path
from mainmenu import MainMenuManager, Transition
from noliictu import Noliictu

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
        pygame.display.set_caption('Time Weaver')
        self.clock = pygame.time.Clock()
        self.running = True

        self.map = pygame.image.load('Assets/Bg/2.png').convert_alpha()
        self.map_scaled = pygame.transform.scale(self.map, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.level = f'{2}-{2}'
        self.level_map = {
            '1-0': "lvl1-0.tmx",
            '1-1': "lvl1-1.tmx",
            '1-2': "lvl1-2.tmx",
            '1-3': "boss1.tmx",
            '2-0': "lvl2-0.tmx",
            '2-1': 'lvl2-1.tmx',
            '2-2': "lvl2-2.tmx",
            '2-3': "noliictu.tmx",
            '5-0': "lvl5.tmx"
        }
        self.mapz = self.level_map.get(self.level, 'test.tmx')

        self.player = Player((0, 0), self.all_sprites, self.collision_sprites)
        self.fix_tmx_tileset('data/maps', 'Assets/Tilesets')
        self.game_active = False
        self.paused = False
        self.transition = Transition(1000)
        self.transition_target = None

        self.menu_manager = MainMenuManager(self.screen, self)
        self.ui = UserInterface(self.screen)

# ========================= Map thingy =========================
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
        self.map_w = map.width * TILE_SIZE
        self.map_h = map.height * TILE_SIZE

        for x, y, image in map.get_layer_by_name('ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for collision in map.get_layer_by_name('pits'):
            CollisionSprite((collision.x, collision.y), pygame.Surface((collision.width, collision.height)), self.collision_sprites)

        self.transition_zones = {}
        self.patrol_zones = []
        for obj in map.get_layer_by_name('zones'):
            if obj.name in ['forward', 'back']:
                self.transition_zones[obj.name] = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            else:
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.patrol_zones.append(rect)

        #player spawn
        spawn_marker = getattr(self, 'respawn_marker', 'Player')
        for marker in map.get_layer_by_name('entities'):
            if marker.name == spawn_marker:
                self.player.rect.midbottom = (marker.x, marker.y)
                self.player.rect.midbottom = (marker.x, marker.y)
                self.player.player_hitbox.center = self.player.rect.center
                self.all_sprites.add(self.player)  # re-add if needed
                self.player.collision_sprites = self.collision_sprites  # update collisions
                self.all_sprites.add(self.player)
                break

        # Setelah player ada, baru spawn musuh
        for marker in map.get_layer_by_name('entities'):
            if marker.name in ['sword', 'axe']:
                enemy = Humanoid(marker.name.capitalize(), (marker.x, marker.y), self.all_sprites, self.collision_sprites)
                enemy.player_ref = self.player
                for zone in self.patrol_zones:
                    if zone.collidepoint(marker.x, marker.y):
                        enemy.patrol_bounds(zone)
                        break
            elif marker.name == 'spear':
                enemy = Humanoid('Spear', (marker.x, marker.y), self.all_sprites, self.collision_sprites)
                enemy.player_ref = self.player
            elif marker.name == 'bookie':
                enemy = Monstrosity((marker.x, marker.y), self.all_sprites, self.collision_sprites, self.player)
            elif marker.name == 'Cervus':
                self.cervus = Cervus((marker.x, marker.y), self.all_sprites, self.player)
            elif marker.name == 'Noliictu':
                self.noliictu = Noliictu((marker.x, marker.y), self.all_sprites, self.player)

    def next_level(self):
        world, stage = map(int, self.level.split('-'))
        next_stage = stage + 1
        next_level_key = f'{world}-{next_stage}'

        # If next stage doesn't exist, go to next world 0
        if next_level_key not in self.level_map:
            world += 1
            next_stage = 0
            next_level_key = f'{world}-{next_stage}'

        self.level = next_level_key
        self.mapz = self.level_map.get(self.level, 'test.tmx')
        self.respawn_marker = 'Player'
        self.transition.start('fade')
        self.transition_target = 'forward'

    def previous_level(self):
        world, stage = map(int, self.level.split('-'))
        prev_stage = max(stage - 1, 0)
        self.level = f'{world}-{prev_stage}'
        self.mapz = self.level_map.get(self.level, 'test.tmx')
        self.respawn_marker = 'Player_back'
        self.player.facing_right = False
        self.transition.start('fade')
        self.transition_target = 'back'

# ========================= GAME LOOP =========================
    def run(self):
        while self.running:
            if not self.paused:
                dt = self.clock.tick(FRAMERATE) / 1000  # proper delta time
            else:
                self.clock.tick(FRAMERATE)
                dt = 0  # freeze updates while paused

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.game_active:
                        self.menu_manager.pause_menu()  # toggle pause

            # Menu control
            if not self.game_active:
                self.menu_manager.main_menu()
                continue

            # Game logic (only if not transitioning and not paused)
            if not self.transition.active and not self.paused:
                self.all_sprites.update(dt)

                # Zone transitions
                if 'forward' in self.transition_zones and self.player.player_hitbox.colliderect(self.transition_zones['forward']):
                    self.next_level()

                if 'back' in self.transition_zones and self.player.player_hitbox.colliderect(self.transition_zones['back']):
                    self.previous_level()

            # Drawing
            self.screen.blit(self.map_scaled, (0, 0))
            self.all_sprites.draw(self.player.rect.center, self.map_w, self.map_h)
            self.ui.draw(self.player)

            # Transition effect (draw on top)
            if self.transition.active:
                self.transition.draw(self.screen)
                self.transition.update(self.clock.get_time())

            # If transition just finished, reset game
            if self.transition_target and not self.transition.active:
                self.reset_game()
                self.transition_target = None

            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()