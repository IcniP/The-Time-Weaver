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
from save_system import SaveManager


def wrap_text(text, font, max_width):
    """Membungkus teks panjang agar muat dalam layar."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())
    return lines


def noliictu_intro_dialogue(game, noliictu):
    game.paused = True
    font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 18)
    max_width = WINDOW_WIDTH - 60  # untuk wrap text

    dialog_lines = [
        "Udara terdistorsi saat pintu marmer terbuka. Sebuah aula luas membentang, langit-langitnya tenggelam dalam bayang. Di tengahnya berdiri ICTU, tangannya terlipat di belakang punggung.",
        "ICTU:\nJadi batas antar realitas akhirnya retak. Aku menghitung butiran pasir, menunggu celahnya menganga... dan ternyata kamulah yang datang. Tak kusangka.",
        "ICTU:\nMendekatlah. Biarkan aku melihat pantulan dunia yang memuntahkanmu. Detak nadimu tidak berasal dari dimensi ini. Rapuh... tapi menggugah.",
        "ICTU:\nTahukah kamu, di mana kakimu berdiri? Ini rahim dari Mundus Devorans, jurang yang akan melahap kerajaan. Aku arsiteknya, pusat dari badai bernama Kiamat.",
        "ICTU:\nKau ragu, bukan? Manusia selalu begitu. Mereka bersandar pada dinding hukum dan dewa yang kini hanya berbisik. Aku akan merobek mereka semua.",
        "ICTU:\nTapi kau... kau tidak ada dalam catatanku. Tak ada nubuat yang menyebut namamu. Kau noda tinta di atas mahakaryaku. Kecelakaan, atau justru pilihan?",
        "ICTU:\nMungkin Takdir yang ketakutan lalu mengirimmu ke sini sebagai taruhan terakhir. Atau... kau adalah pilihan yang tak terhitungkan. Dan aku menyukai ketidakpastian.",
        "ICTU:\nKau merasakannya, bukan? Dunia ini sudah tak mampu menanggung deritanya sendiri. Aku akan merobek kulitnya, membakar semua aturan. Di dalam kobaran itu, rasa sakit tak akan lagi punya bahasa.",
        "ICTU:\nMinggirlah dan saksikan. Atau angkat senjatamu dan jadi nada pertama dari requiem semesta. Keduanya akan berujung pada kehancuran.",
        "ICTU:\nSekarang... mari kita uji siapa di antara kita yang memang pantas untuk ada."
    ]

    current_line = 0

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if event.type == pygame.KEYDOWN and event.key not in (pygame.K_SPACE, pygame.K_RETURN):
                    continue
                current_line += 1

        if current_line >= len(dialog_lines):
            break

        # GAMESCENE DITAMPILKAN dulu
        game.screen.blit(game.map_scaled, (0, 0))
        game.draw_parallax_layers(game.player.rect.center)
        game.all_sprites.draw(game.player.rect.center, game.map_w, game.map_h)
        game.draw_branches_layer(game.player.rect.center)
        game.ui.draw(game.player)

        # DIALOG BOX
        wrapped = wrap_text(dialog_lines[current_line], font, max_width)
        box_rect = pygame.Rect(20, WINDOW_HEIGHT - 100, WINDOW_WIDTH - 40, 80)
        pygame.draw.rect(game.screen, (0, 0, 0), box_rect)
        pygame.draw.rect(game.screen, (255, 255, 255), box_rect, 2)

        line_spacing = 26  # jarak antar baris
        text_top_margin = 12  # padding dari atas box

        for i, line in enumerate(wrapped):
            text_surface = font.render(line, True, 'white')
            game.screen.blit(text_surface, (box_rect.left + 10, box_rect.top + text_top_margin + i * line_spacing))

        pygame.display.update()
        game.clock.tick(FRAMERATE)

    game.paused = False


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
        pygame.display.set_caption('Time Weaver')
        self.clock = pygame.time.Clock()
        self.running = True

        #sprite groups----------------------------------------
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.spike_sprites = pygame.sprite.Group()

        #level thingy----------------------------------------
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
        self.set_checkpoint("2-0")
        self.bg_folder_map = {
            '1': 'outdoor',
            '2': 'castle',
            '3': 'forest'
        }

        #background n parallax layers----------------------------------------
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

        #create playa n camera----------------------------------------
        camera_group = self.all_sprites
        self.player = Player((0, 0), self.all_sprites, self.collision_sprites, camera_group)
        self.player.game = self

        #camera shake when attack thingy----------------------------------------
        self.shake_duration = 0
        self.shake_timer = 0
        self.shake_intensity = 2
        self.shake_offset = pygame.Vector2(0, 0)

        self.fix_tmx_tileset('data/maps', 'Assets/Tilesets')
        self.game_active = False
        self.paused = False
        #transition thingy----------------------------------------
        self.transition = Transition(2000)
        self.transition_target = None
        #main menu n ui thingy----------------------------------------
        self.menu_manager = MainMenuManager(self.screen, self)
        self.ui = UserInterface(self.screen)

        self.cervus_hp_bar = BossHealthBar(max_health=800, length=400, pos=(WINDOW_WIDTH//2 - 200, 320), name="Cervus The Devourer")
        self.noliictu_hp_bar = BossHealthBar(max_health=3000, length=400, pos=(WINDOW_WIDTH//2 - 200, 320), name ="Noliictu The One who stands above all")

        #checkpoints n respawn thingy----------------------------------------
        self.respawn_marker = 'Player'
        self.respawn_data = {
            'map_key': self.level,
            'marker_name': 'Player'
        }

    def set_checkpoint(self, chk:str):
        self.level = chk                          
        self.mapz  = self.level_map.get(chk, 'test.tmx')

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

    #reset game when dying / transitioning between levels
    def reset_game(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.spike_sprites.empty()
        self.map1()
    #method untuk load map ny------------------------------
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

        cervus_marker = None
        for marker in map.get_layer_by_name('entities'):
            if marker.name == spawn_marker:
                self.player.rect.midbottom = (marker.x, marker.y)
                self.player.player_hitbox.center = self.player.rect.center
                self.all_sprites.add(self.player)
                self.player.collision_sprites = self.collision_sprites
            elif marker.name == 'Cervus':
                cervus_marker = marker

        # Enemy and boss entities
        for marker in map.get_layer_by_name('entities'):
            if marker.name in ['sword', 'axe']:
                skelly_slash = Humanoid(marker.name.capitalize(), (marker.x, marker.y), self.all_sprites, self.collision_sprites)
                skelly_slash.player_ref = self.player
                for zone in self.patrol_zones:
                    if zone.collidepoint(marker.x, marker.y):
                        skelly_slash.patrol_bounds(zone)
                        break
            elif marker.name == 'spear':
                skelly_thrust = Humanoid('Spear', (marker.x, marker.y), self.all_sprites, self.collision_sprites)
                skelly_thrust.player_ref = self.player
            elif marker.name == 'bookie':
                bookie = Monstrosity((marker.x, marker.y), self.all_sprites, self.collision_sprites, self.player)
            elif marker.name == 'wraith':
                self.range_rect = None
                for r in self.range_rects:
                    if r.collidepoint(marker.x, marker.y):
                        self.range_rect = r
                        break
                wraith = Fly((marker.x, marker.y), self.all_sprites, self.collision_sprites, self.player, self.range_rect)
            elif marker.name == 'Noliictu':
                self.noliictu = Noliictu((marker.x, marker.y), self.all_sprites, self.player)
                noliictu_intro_dialogue(self, self.noliictu)

        # Spawn Cervus after player to ensure it's placed behind
        if cervus_marker:
            self.cervus = Cervus((self.player.rect.centerx - 80, self.player.rect.top - 96), self.all_sprites, self.player, self.collision_sprites)
            self.all_sprites.add(self.cervus)
            if hasattr(self.cervus.current_phase, 'main_body'):
                self.all_sprites.add(self.cervus.current_phase.main_body, layer='behind_ground')
            if hasattr(self.cervus.current_phase, 'main_body'):
                self.all_sprites.add(self.cervus.current_phase.main_body, layer='behind_ground')


    #method utk nampilin gambar2 buat parallaxny---------------------
    def draw_parallax_layers(self, target_pos):
        for image, speed in self.parallax_layers:
            image_width = image.get_width()
            offset_x = (target_pos[0] - self.map_w // 2) * speed
            draw_x = -offset_x + (WINDOW_WIDTH // 2 - image_width // 2)
            self.screen.blit(image, (draw_x, 0))

    #method utk nampilin gambar parallax branchesny,-------------------- 
    #karna di layer atas segalany jdiny dipisah
    def draw_branches_layer(self, target_pos):
        image = self.branches_above
        speed = self.branches_above_speed
        image_width = image.get_width()
        offset_x = (target_pos[0] - self.map_w // 2) * speed
        draw_x = -offset_x + (WINDOW_WIDTH // 2 - image_width // 2)
        self.screen.blit(image, (draw_x, 0))

    #method utk pindah kedepan level/mapny---------------------------
    def next_level(self):
        world, stage = map(int, self.level.split('-'))
        next_stage = stage + 1
        next_key = f"{world}-{next_stage}"
        if next_key not in self.level_map:
            world += 1
            next_key = f"{world}-0"

        self.set_checkpoint(next_key)
        self.respawn_marker = 'Player'
        self.transition.start('fade')
        self.transition_target = 'forward'

    #method utk mundur level/mapny-----------------------------------
    def previous_level(self):
        world, stage = map(int, self.level.split('-'))
        prev_stage = stage - 1
        if prev_stage < 0:
            world -= 1
            prev_stage = max(
                int(k.split('-')[1]) for k in self.level_map
                if k.startswith(f"{world}-")
            )
        self.set_checkpoint(f"{world}-{prev_stage}")   # ← pakai helper
        self.respawn_marker = 'Player_back'
        self.player.facing_right = False
        self.transition.start('fade')
        self.transition_target = 'back'

    def load_game_slot(self, slot:int):
        data = SaveManager.load_game(slot)
        if not data:
            print("❌ Save tidak ditemukan / rusak"); return

        # ganti map bila checkpoint beda
        if self.level != data["checkpoint"]:
            self.set_checkpoint(data["checkpoint"])   
            self.reset_game()
            self.update_background_assets()

        # pulihkan posisi & stats
        self.player.rect.topleft = tuple(data["position"])
        self.player.hp      = data["hp"]
        self.player.stamina = data["stamina"]
        if "level" in data and hasattr(self.player, "level"):
            self.player.level = data["level"]

        # ── print aman ──
        lvl_str = getattr(self.player, "level", "?")
        print(f"✔  Slot {slot} loaded — LV{lvl_str} @ {self.level}")

        self.game_active = True

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

    #method run utama gameny-----------------------------------------
    def run(self):
        while self.running:
            if not self.paused:
                dt = self.clock.tick(FRAMERATE) / 1000
            else:
                self.clock.tick(FRAMERATE)
                dt = 0

            #events2 ny
            for event in pygame.event.get():
                #klo klik close button, gameny ditutup
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                #klo mencet tombol escape, gameny di pause
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.game_active:
                        self.menu_manager.pause_menu()
            #klo mencet e pas collide sma rect checkpoint, respawnny jdi disitu
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
                #ngejalanin semua method update class yg objek2ny di group all_sprites
                self.all_sprites.update(dt)
                #shake_timerny di assign di player.start_attack()
                if self.shake_timer > 0:
                    self.shake_timer -= dt
                    self.shake_offset.x = random.randint(-self.shake_intensity, self.shake_intensity)
                    self.shake_offset.y = random.randint(-self.shake_intensity, self.shake_intensity)
                else:
                    self.shake_offset = pygame.Vector2(0, 0)

                for spike in self.spike_sprites:
                    #ngecek collision player sama rect2 spikes
                    if spike.rect.colliderect(self.player.player_hitbox):
                        self.player.die()
                        break

                    #ngecek collision spike sama rect2 Humanoid(skellies) n Mosntrosity(Bookie)
                    for sprite in self.all_sprites:
                        if isinstance(sprite, (Humanoid, Monstrosity)):
                            hitbox = getattr(sprite, 'entity_hitbox', getattr(sprite, 'hitbox', sprite.rect))
                            if spike.rect.colliderect(hitbox):
                                if hasattr(sprite, 'die'):
                                    sprite.die(instant=True)

                #utk pindah antar levelny
                if 'forward' in self.transition_zones and self.player.player_hitbox.colliderect(self.transition_zones['forward']):
                    self.next_level()
                    self.update_background_assets()
                if 'back' in self.transition_zones and self.player.player_hitbox.colliderect(self.transition_zones['back']):
                    self.previous_level()
                    self.update_background_assets()

            if hasattr(self, 'cervus'):
                self.cervus.update(dt)
                if hasattr(self.cervus.current_phase, 'main_body'):
                    if self.cervus.current_phase.main_body not in self.all_sprites:
                        self.all_sprites.add(self.cervus.current_phase.main_body)

            self.screen.blit(self.map_scaled, (0, 0))
            self.draw_parallax_layers(self.player.rect.center)
            self.all_sprites.draw(self.player.rect.center + self.shake_offset, self.map_w, self.map_h)
            self.draw_branches_layer(self.player.rect.center)
            self.ui.draw(self.player)

            if hasattr(self, 'cervus') and hasattr(self.cervus.current_phase, 'main_body'):
                self.cervus_hp_bar.update(self.cervus.current_phase.main_body.hp)
                self.cervus_hp_bar.draw(self.screen)

            if hasattr(self, 'noliictu') and self.noliictu.alive():
                self.noliictu_hp_bar.update(self.noliictu.hp)
                self.noliictu_hp_bar.draw(self.screen)

            if self.transition.active:
                self.transition.draw(self.screen)
                self.transition.update(self.clock.get_time())

             #respawn thingy
            if self.transition_target and not self.transition.active:
                if self.transition_target == 'respawn':
                    self.player.dead = False
                    self.player.set_hp(self.player.max_hp)
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