from settings import *
from player import Player
from humanoid import Humanoid
from monstrosity import Monstrosity
from fly import Fly
from entity import AllSprites, Sprite
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

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.spike_sprites = pygame.sprite.Group()

        self.level = f'{3}-{0}'
        self.level_map = {
            '1-0': "lvl1-0.tmx",
            '1-1': "lvl1-1.tmx",
            '1-2': "lvl1-2.tmx",
            '1-3': "lvl2-0.tmx",
            '2-0': "noliictu.tmx",
            '3-0': 'lvl2-1.tmx',
            '3-1': "lvl2-2.tmx",
            '3-2': "lvl3-0.tmx",
            '3-3': "lvl3-1.tmx",
            '3-4': "lvl3-2.tmx",
            '3-5': "cervus.tmx"
        }

        self.bg_folder_map = {
            '1': 'outdoor',
            '2': 'castle',
            '3': 'forest'
        }
        self.mapz = self.level_map.get(self.level, 'test.tmx')

        folder_name = self.bg_folder_map.get(self.level.split('-')[0], 'default')
        self.map = pygame.image.load(f'Assets/Bg/{folder_name}/0.png').convert_alpha()
        self.map_scaled = pygame.transform.scale(self.map, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.parallax_layers = [
            (pygame.image.load(f'Assets/Bg/{folder_name}/1.png').convert_alpha(), 0.2),
            (pygame.image.load(f'Assets/Bg/{folder_name}/2.png').convert_alpha(), 0.3),
            (pygame.image.load(f'Assets/Bg/{folder_name}/3.png').convert_alpha(), 0.4),
            (pygame.image.load(f'Assets/Bg/{folder_name}/4.png').convert_alpha(), 0.5),
        ]

        self.branches_above = pygame.image.load(f'Assets/Bg/{folder_name}/5.png').convert_alpha()
        self.branches_above_speed = 0.6

        camera_group = self.all_sprites
        self.player = Player((0, 0), self.all_sprites, self.collision_sprites, camera_group)
        self.player.game = self

        self.shake_duration = 0
        self.shake_timer = 0
        self.shake_intensity = 2
        self.shake_offset = pygame.Vector2(0, 0)

        self.fix_tmx_tileset('data/maps', 'Assets/Tilesets')
        self.game_active = False
        self.paused = False
        self.transition = Transition(2000)
        self.transition_target = None
        self.menu_manager = MainMenuManager(self.screen, self)
        self.ui = UserInterface(self.screen)

        self.respawn_marker = 'Player'
        self.respawn_data = {
            'map_key': self.level,
            'marker_name': 'Player'
        }

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
        self.spike_sprites.empty()
        self.map1()

    def map1(self):
        map = load_pygame(join('data', 'maps', self.mapz))
        self.map_w = map.width * TILE_SIZE
        self.map_h = map.height * TILE_SIZE

        self.range_rects = [pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                            for obj in map.get_layer_by_name('range')]

        for x, y, image in map.get_layer_by_name('ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for pit in map.get_layer_by_name('pits'):
            spike_rect = pygame.Rect(pit.x, pit.y, pit.width, pit.height)
            spike = pygame.sprite.Sprite(self.spike_sprites)
            spike.rect = spike_rect
            spike.image = pygame.Surface((pit.width, pit.height))

        for x, y, image in map.get_layer_by_name('spikes').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.spike_sprites))

        for x, y, image in map.get_layer_by_name('things').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        self.transition_zones = {}
        self.patrol_zones = []
        for obj in map.get_layer_by_name('zones'):
            if obj.name in ['forward', 'back']:
                self.transition_zones[obj.name] = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            else:
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.patrol_zones.append(rect)
        
        self.checkpoints = []
        for obj in map.get_layer_by_name('zones'):
            if obj.name == 'checkpoint':
                self.checkpoints.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        if self.transition_target == 'respawn':
            spawn_marker = self.respawn_data.get('marker_name', 'Player')
        else:
            spawn_marker = getattr(self, 'respawn_marker', 'Player')

        for marker in map.get_layer_by_name('entities'):
            if marker.name == spawn_marker:
                self.player.rect.midbottom = (marker.x, marker.y)
                self.player.player_hitbox.center = self.player.rect.center
                self.all_sprites.add(self.player)
                self.player.collision_sprites = self.collision_sprites
                break

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
            elif marker.name == 'wraith':
                self.range_rect = None
                for r in self.range_rects:
                    if r.collidepoint(marker.x, marker.y):
                        self.range_rect = r
                        break
                enemy = Fly((marker.x, marker.y), self.all_sprites, self.collision_sprites, self.player, self.range_rect)
            elif marker.name == 'Noliictu':
                self.noliictu = Noliictu((marker.x, marker.y), self.all_sprites, self.player)
            elif marker.name == 'Cervus':
                self.cervus = Cervus((marker.x, marker.y), self.all_sprites, self.player, self.collision_sprites)
                self.all_sprites.add(self.cervus)

                if hasattr(self.cervus.current_phase, 'main_body'):
                    self.all_sprites.add(self.cervus.current_phase.main_body)

    def draw_parallax_layers(self, target_pos):
        for image, speed in self.parallax_layers:
            image_width = image.get_width()
            offset_x = (target_pos[0] - self.map_w // 2) * speed
            draw_x = -offset_x + (WINDOW_WIDTH // 2 - image_width // 2)
            self.screen.blit(image, (draw_x, 0))

    def draw_branches_layer(self, target_pos):
        image = self.branches_above
        speed = self.branches_above_speed
        image_width = image.get_width()
        offset_x = (target_pos[0] - self.map_w // 2) * speed
        draw_x = -offset_x + (WINDOW_WIDTH // 2 - image_width // 2)
        self.screen.blit(image, (draw_x, 0))

    def next_level(self):
        world, stage = map(int, self.level.split('-'))
        next_stage = stage + 1
        next_level_key = f'{world}-{next_stage}'
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
        prev_stage = stage - 1
        if prev_stage < 0:
            world -= 1
            candidate_stages = [int(k.split('-')[1]) for k in self.level_map if k.startswith(f"{world}-") and k.split('-')[1].isdigit()]
            prev_stage = max(candidate_stages) if candidate_stages else 0
        self.level = f'{world}-{prev_stage}'
        self.mapz = self.level_map.get(self.level, 'test.tmx')
        self.respawn_marker = 'Player_back'
        self.player.facing_right = False
        self.transition.start('fade')
        self.transition_target = 'back'

    def update_background_assets(self):
        folder_name = self.bg_folder_map.get(self.level.split('-')[0], 'default')

        self.map = pygame.image.load(f'Assets/Bg/{folder_name}/0.png').convert_alpha()
        self.map_scaled = pygame.transform.scale(self.map, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.parallax_layers = [
            (pygame.image.load(f'Assets/Bg/{folder_name}/1.png').convert_alpha(), 0.2),
            (pygame.image.load(f'Assets/Bg/{folder_name}/2.png').convert_alpha(), 0.3),
            (pygame.image.load(f'Assets/Bg/{folder_name}/3.png').convert_alpha(), 0.4),
            (pygame.image.load(f'Assets/Bg/{folder_name}/4.png').convert_alpha(), 0.5),
        ]

        self.branches_above = pygame.image.load(f'Assets/Bg/{folder_name}/5.png').convert_alpha()

    def run(self):
        while self.running:
            if not self.paused:
                dt = self.clock.tick(FRAMERATE) / 1000
            else:
                self.clock.tick(FRAMERATE)
                dt = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.game_active:
                        self.menu_manager.pause_menu()
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]:
                for checkpoint in self.checkpoints:
                    if checkpoint.colliderect(self.player.player_hitbox):
                        self.respawn_data = {
                            'map_key': self.level,
                            'marker_name': 'Player_rest'
                        }
                        print("Checkpoint activated!")

            if not self.game_active:
                self.menu_manager.main_menu()
                continue

            if not self.transition.active and not self.paused:
                self.all_sprites.update(dt)
                if self.shake_timer > 0:
                    self.shake_timer -= dt
                    self.shake_offset.x = random.randint(-self.shake_intensity, self.shake_intensity)
                    self.shake_offset.y = random.randint(-self.shake_intensity, self.shake_intensity)
                else:
                    self.shake_offset = pygame.Vector2(0, 0)

                for spike in self.spike_sprites:
                    if spike.rect.colliderect(self.player.player_hitbox):
                        self.player.die()
                        break

                    for sprite in self.all_sprites:
                        if isinstance(sprite, (Humanoid, Monstrosity)):
                            hitbox = getattr(sprite, 'entity_hitbox', getattr(sprite, 'hitbox', sprite.rect))
                            if spike.rect.colliderect(hitbox):
                                if hasattr(sprite, 'die'):
                                    sprite.die(instant=True)

                if 'forward' in self.transition_zones and self.player.player_hitbox.colliderect(self.transition_zones['forward']):
                    self.next_level()
                    self.update_background_assets()
                if 'back' in self.transition_zones and self.player.player_hitbox.colliderect(self.transition_zones['back']):
                    self.previous_level()
                    self.update_background_assets()

            if hasattr(self, 'cervus'):
                self.cervus.update(dt)
                if hasattr(self.cervus.current_phase, 'main_body'):
                    self.all_sprites.add(self.cervus.current_phase.main_body)

            self.screen.blit(self.map_scaled, (0, 0))
            self.draw_parallax_layers(self.player.rect.center)
            self.all_sprites.draw(self.player.rect.center + self.shake_offset, self.map_w, self.map_h)
            self.draw_branches_layer(self.player.rect.center)
            self.ui.draw(self.player)

            if self.transition.active:
                self.transition.draw(self.screen)
                self.transition.update(self.clock.get_time())

            if self.transition_target and not self.transition.active:
                if self.transition_target == 'respawn':
                    self.player.dead = False
                    self.player.hp = self.player.max_hp
                    self.player.knives = self.player.max_knives
                    self.update_background_assets()

                    # Go to checkpoint map
                    self.level = self.respawn_data.get('map_key', '1-0')
                    self.mapz = self.level_map.get(self.level, 'test.tmx')

                    self.reset_game()
                    self.transition_target = None
                    self.transition.fade_reason = None
                else:
                    self.reset_game()
                    self.transition_target = None

            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
