import pygame
from settings import *
from bossbase import BossBase
from os.path import join


class Cervus(BossBase):
    def __init__(self, pos, groups, collision_sprites, player):
        animation_paths = {
            'Idle': ['cervus', 'deer', 'idle'],
            'Walk': ['cervus', 'deer', 'walk'],
            'Dash': ['cervus', 'deer', 'dash'],
            'Stomp': ['cervus', 'deer', 'stomp'],
            'Stomp_Smear': ['cervus', 'deer', 'stomp_smear']
        }
        super().__init__(pos, groups, player, boss_name='Cervus', animation_paths=animation_paths)

        self.collision_sprites = collision_sprites
        self.groupss = groups

        self.entity_hitbox = pygame.Rect(0, 0, 40, 40)
        self.entity_hitbox.center = self.rect.center

        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 80
        self.gravity = 30
        self.facing_right = True

        self.hp = 10
        self.death_time = 0
        self.death_duration = 400

        # Wander bounds from spawn
        self.left_bound = self.rect.centerx - TILE_SIZE * 6
        self.right_bound = self.rect.centerx + TILE_SIZE * 6

        # AI control flag
        self.wandering = True

    def move(self, dt):
        player_x = self.player.rect.centerx
        cervus_x = self.rect.centerx
        distance_x = abs(player_x - cervus_x)

        # Chase if player within 6 tiles; wander otherwise
        if distance_x <= TILE_SIZE * 6:
            self.wandering = False
        elif distance_x > TILE_SIZE * 8:
            self.wandering = True

        if self.wandering:
            # Simple left-right patrol
            if self.rect.centerx <= self.left_bound:
                self.direction.x = 1
            elif self.rect.centerx >= self.right_bound:
                self.direction.x = -1
        else:
            # Chase the player
            self.direction.x = 1 if player_x > cervus_x else -1

        self.facing_right = self.direction.x > 0

        # Apply horizontal movement
        self.entity_hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.rect.center = self.entity_hitbox.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.entity_hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.entity_hitbox.right = sprite.rect.left
                    elif self.direction.x < 0:
                        self.entity_hitbox.left = sprite.rect.right
        self.rect.center = self.entity_hitbox.center

    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt
        self.entity_hitbox.y += self.direction.y
        self.collision('vertical')
        self.rect.center = self.entity_hitbox.center

    def update_state(self):
        self.status = 'Walk' if self.direction.x != 0 else 'Idle'

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.death_time = pygame.time.get_ticks()
            mask = pygame.mask.from_surface(self.image)
            surf = mask.to_surface(setcolor=(255, 100, 0), unsetcolor=(0, 0, 0, 0))
            surf.set_colorkey((0, 0, 0))
            self.image = surf
            self.direction = pygame.Vector2(0, 0)

    def update(self, dt):
        now = pygame.time.get_ticks()
        if self.death_time == 0:
            self.entity_hitbox.center = self.rect.center
            self.move(dt)
            self.add_gravity(dt)
            self.update_state()
            self.animate(dt)
        elif now - self.death_time >= self.death_duration:
            self.kill()
