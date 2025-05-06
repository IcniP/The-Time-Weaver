import pygame
from settings import *
from os import listdir
from os.path import join, dirname, abspath

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
        self.mask = pygame.mask.from_surface(self.image)  # Create mask for accurate collision

        # Health points (HP) for the boss
        self.hp = 100  # Default HP for any boss

        # Damage control
        self.is_damaged = False  # Track if already hit by an attack

    def import_assets(self, animation_paths):
        base_path = join(dirname(abspath(__file__)), '..', 'Assets', 'Enemy', 'Final')
        for key, relative_path in animation_paths.items():
            full_path = join(base_path, *relative_path)
            self.animations[key] = self.import_folder(full_path)

    def import_folder(self, path):
        images = []
        for file_name in sorted(listdir(path), key=lambda x: int(x.split('.')[0])):
            full_path = join(path, file_name)
            image = pygame.image.load(full_path).convert_alpha()
            images.append(image)
        return images

    def animate(self, dt):
        frames = self.animations[self.status]
        self.frame_index += self.animation_speed * dt

        if self.frame_index >= len(frames):
            self.frame_index = 0

        self.image = frames[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)  # Update mask every frame

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

        # Only detect if the player is attacking
        if not self.player.attacking:
            self.is_damaged = False
            return

        attack_hitbox = self.player.attack_hitbox()
        if attack_hitbox.width <= 0 or attack_hitbox.height <= 0:
            return

        attack_mask = pygame.Mask(attack_hitbox.size, fill=True)
        offset = (attack_hitbox.x - self.rect.x, attack_hitbox.y - self.rect.y)
        if self.mask.overlap(attack_mask, offset):
            if not self.is_damaged:
                self.take_damage(500)  # You can later set variable damage if needed
                self.is_damaged = True
                print(f"{self.boss_name} collided with the player's attack! HP: {self.hp}")
        else:
            self.is_damaged = False

    def update(self, dt):
        self.animate(dt)
        self.check_collision_with_player()
