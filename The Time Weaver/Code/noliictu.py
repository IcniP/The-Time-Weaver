import pygame
from settings import *
from entity import *
from bossbase import BossBase
from os.path import join
import random
import math

class Knive(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos, groups, player):
        super().__init__(groups)

        num = random.randint(0, 3)
        original_image = pygame.image.load(join('Assets', 'Enemy', 'noliictu', 'Knive', f'{num}.png')).convert_alpha()

        self.start_pos = pygame.math.Vector2(pos)
        self.player = player

        direction_vector = pygame.math.Vector2(target_pos) - self.start_pos
        self.direction = direction_vector.normalize()

        angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(original_image, -angle)
        self.rect = self.image.get_rect(center=pos)

        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 200 #projectile speed
        self.damage = 1  # Damage ke player

    def update(self, dt):
        move = self.direction * self.speed * dt
        self.rect.centerx += move.x
        self.rect.centery += move.y

        # Cek jarak
        current_pos = pygame.math.Vector2(self.rect.center)
        if self.start_pos.distance_to(current_pos) >= 500:
            self.kill()
            return

        if pygame.sprite.collide_mask(self, self.player):
            self.player.take_damage(self.damage)
            self.kill()

class Noliictu(BossBase):
    def __init__(self, pos, groups, player):
        animation_paths = {
            'Idle': ['noliictu', 'Idle'],
            'Attack': ['noliictu', 'Attack'],
            'Knive': ['noliictu', 'Knive'],
            'TeleportIn': ['noliictu', 'TeleportIn'],
            'TeleportOut': ['noliictu', 'TeleportOut'],
            'Ult': ['noliictu', 'Ult'],
            'UltIn': ['noliictu', 'UltIn']
        }
        super().__init__(pos, groups, player, boss_name='Noliictu', animation_paths=animation_paths)

        self.hp = 3000
        self.detection_rect = pygame.Rect(self.rect.centerx - 100, self.rect.centery - 100, 200, 200)
        self.detection_active = False
        self.time_in_rect = 0
        self.teleporting = False
        self.teleport_cooldown = 10
        self.ready_to_teleport = False

        self.knive_group = groups  

        # attack attributes
        self.attack_cooldown = 5
        self.attack_cooldown_timer = 0
        self.knife_timer = 0
        self.knives_fired = 0
        self.max_knives = 4
        self.knife_interval = 0.8  
        self.attacking = False

    def attack(self, dt):
        if not self.attacking:
            self.attacking = True
            self.knives_fired = 0
            self.knife_timer = 0
            self.play_animation('Attack')

        self.knife_timer += dt
        if self.knife_timer >= self.knife_interval and self.knives_fired < self.max_knives:
            self.knife_timer = 0
            self.knives_fired += 1

            offset = pygame.Vector2(70, 0) if self.player.rect.centerx > self.rect.centerx else pygame.Vector2(-70, 0)
            spawn_pos = pygame.Vector2(self.rect.center) - offset
            Knive(spawn_pos, self.player.player_hitbox.midbottom, [self.knive_group], self.player)

        if self.knives_fired >= self.max_knives:
            self.attacking = False
            self.attack_cooldown_timer = 0
            self.play_animation('Idle')

    def update(self, dt):
        super().update(dt)
        self.detection_rect.center = self.rect.center

        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt

        # === Handle teleport ===
        if self.teleporting:
            frames = self.animations[self.status]
            if self.status == 'TeleportOut' and self.frame_index >= len(frames) - 1:
                self.play_animation('TeleportIn')
            elif self.status == 'TeleportIn' and self.frame_index >= len(frames) - 1:
                self.teleporting = False
                self.teleport_cooldown = 10  # cooldown TP 10 detik
                self.attack_cooldown_timer = self.attack_cooldown  # Langsung siap untuk attack
                self.attacking = False
                if self.status != 'Idle':
                    self.play_animation('Idle')
        else:
            if self.detection_rect.colliderect(self.player.rect):
                self.time_in_rect += dt
            else:
                self.time_in_rect = 0

            if self.time_in_rect >= 5 and self.teleport_cooldown <= 0:
                self.play_animation('TeleportOut')
                self.teleporting = True
                self.attacking = False
                self.time_in_rect = 0
            else:
                if self.attacking:
                    self.attack(dt)
                else:
                    self.attack_cooldown_timer += dt
                    if self.attack_cooldown_timer >= self.attack_cooldown:
                        self.attack(dt)
                    elif self.status != 'Idle':
                        self.play_animation('Idle')

    def draw_detection_rect(self, surface):
        if self.detection_active:
            pygame.draw.rect(surface, (255, 0, 0), self.detection_rect, 2)
