from settings import *


class BossBase(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, boss_name, animation_paths):
        super().__init__(groups)
        self.player = player
        self.boss_name = boss_name
        self.animations = {key: [] for key in animation_paths.keys()}
        self.import_assets(animation_paths)
        self.status = 'Idle'
        self.frame_index = 0
        self.animation_speed = 6

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.hp = 100

        self.is_damaged = False

        self.facing_right = True

    def import_assets(self, animation_paths):
        for key, relative_path in animation_paths.items():
            base_path = join('Assets', 'Enemy', *relative_path)
            self.animations[key] = self.import_folder(base_path)

    def import_folder(self, path):
        images = []
        for file_name in sorted(listdir(path), key=lambda x: int(x.split('.')[0])):
            full_path = join(path, file_name)
            image = pygame.image.load(full_path).convert_alpha()
            images.append(image)
        return images

    def animate(self, dt):
        if self.player.rect.centerx < self.rect.centerx:
            self.facing_right = False
        else:
            self.facing_right = True

        frames = self.animations[self.status]
        self.frame_index += self.animation_speed * dt

        if self.frame_index >= len(frames):
            self.frame_index = 0

        original_image = frames[int(self.frame_index)]

        # Flip kalau perlu
        if self.facing_right:
            self.image = original_image
        else:
            self.image = pygame.transform.flip(original_image, True, False)

        self.mask = pygame.mask.from_surface(self.image)

    def play_animation(self, animation_name):
        if animation_name in self.animations:
            self.status = animation_name
            self.frame_index = 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.die()

    def die(self):
        print(f"{self.boss_name} has been defeated!")
        self.kill()

    def check_collision_with_player(self):
        if not self.alive():
            return

        if not self.player.attacking:
            self.is_damaged = False
            return

        attack_hitbox = self.player.attack_hitbox()
        if attack_hitbox.width != 0 or attack_hitbox.height != 0:
            return

    def update(self, dt):
        self.animate(dt)
        self.check_collision_with_player()
