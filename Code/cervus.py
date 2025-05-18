import pygame
from settings import *
from bossbase import BossBase

class Cervus(BossBase):
    def __init__(self, pos, groups, player, collision_sprites=None):
        animation_paths = {
            'Idle': ['cervus', '1st'],
            'Idle2': ['cervus', '2nd'],
            'Deeridle': ['cervus', 'deer', 'idle'],
            'Deerwalk': ['cervus', 'deer', 'walk'],
            'Deerstomp': ['cervus', 'deer', 'stomp'],
            'Deerdash': ['cervus', 'deer', 'dash'],
            'Hand': ['cervus', 'hand', 'idle'],
            'Handattack1': ['cervus', 'hand', 'a1'],
            'Handattack2': ['cervus', 'hand', 'a2']
        }

        super().__init__(pos, groups, player, boss_name='Cervus', animation_paths=animation_paths)

        self.hp = 5
        self.phase = 1

        self.cooldowns = {'stomp': 0, 'dash': 0, 'left': 0, 'right': 0}
        self.cooldown_time = {'stomp': 30000, 'dash': 15000, 'left': 3000, 'right': 3000}
        self.attack_in_progress = False
        self.attack_end_time = 0

        self.speed = 40
        self.gravity = 30
        self.direction = pygame.Vector2(0, 0)
        self.jumping = False

        self.rect = self.image.get_rect(midbottom=pos)

        # Buat entity_hitbox sebagai atribut utama yang dipakai player
        self.rect = self.image.get_rect(midbottom=pos)
        self.deer_hitbox = pygame.Rect(0, 0, 32, 32)
        self.deer_hitbox.midbottom = self.rect.midbottom  
        self.entity_hitbox = self.deer_hitbox.inflate(20, 0)
        self.entity_hitbox.center = self.deer_hitbox.center

        self.collision_sprites = collision_sprites or pygame.sprite.Group()

        # Hands
        self.left_hand = pygame.sprite.Sprite()
        self.right_hand = pygame.sprite.Sprite()
        self.left_hand.image = self.animations['Hand'][0]
        self.right_hand.image = pygame.transform.flip(self.animations['Hand'][0], True, False)
        self.left_hand.rect = self.left_hand.image.get_rect(center=self.rect.center)
        self.right_hand.rect = self.right_hand.image.get_rect(center=self.rect.center)
        self.hand_speed = 60
        self.hands_active = False
        if isinstance(groups, (tuple, list)):
            for g in groups:
                self.add(g)
        else:
            self.add(groups)

        player.groupss.add(self)


    # ---------------------------- Phase 1: Deer ----------------------------

    def move(self): 
        pass
    def move_to_player(self, dt):
        if self.attack_in_progress:
            self.direction.x = 0
            return

        if abs(self.rect.centerx - self.player.rect.centerx) > 10:
            self.direction.x = 1 if self.player.rect.centerx > self.rect.centerx else -1
            self.status = 'Deerwalk'
        else:
            self.direction.x = 0
            self.status = 'Deeridle'

        self.facing_right = self.direction.x > 0

    def perform_attack(self):
        now = pygame.time.get_ticks()
        if self.attack_in_progress and now >= self.attack_end_time:
            self.attack_in_progress = False
            return

        if not self.attack_in_progress:
            if now - self.cooldowns['stomp'] >= self.cooldown_time['stomp']:
                self.status = 'Deerstomp'
                self.cooldowns['stomp'] = now
                self.attack_in_progress = True
                self.attack_end_time = now + 800
                self.damage_player()
            elif now - self.cooldowns['dash'] >= self.cooldown_time['dash']:
                self.status = 'Deerdash'
                self.cooldowns['dash'] = now
                self.attack_in_progress = True
                self.attack_end_time = now + 800
                self.damage_player()

    def damage_player(self):
        if self.rect.colliderect(self.player.player_hitbox):
            self.player.take_damage(1)

    # ---------------------------- Physics like Player ----------------------------

    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt
        self.deer_hitbox.y += self.direction.y
        self.collision('vertical')

        self.deer_hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        self.rect.center = self.deer_hitbox.center
        self.entity_hitbox.center = self.deer_hitbox.center  # PENTING!

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.deer_hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.deer_hitbox.right = sprite.rect.left
                    elif self.direction.x < 0:
                        self.deer_hitbox.left = sprite.rect.right
                    self.direction.x = 0
                elif direction == 'vertical':
                    if self.direction.y > 0:
                        self.deer_hitbox.bottom = sprite.rect.top
                        self.direction.y = 0
                        self.jumping = False
                    elif self.direction.y < 0:
                        self.deer_hitbox.top = sprite.rect.bottom
                        self.direction.y = 0

        self.rect.center = self.deer_hitbox.center

    # ---------------------------- Phase 2: Hands ----------------------------

    def phase2_setup(self):
        self.hp = 800
        self.phase = 2
        self.status = 'Idle2'
        self.direction.x = 0
        self.hands_active = True

        self.left_hand.rect.center = self.rect.center
        self.right_hand.rect.center = self.rect.center

        if hasattr(self.left_hand, 'add'):
            self.left_hand.add(self.groups())
            self.right_hand.add(self.groups())

    def move_hand(self, hand, is_left, dt):
        now = pygame.time.get_ticks()
        side = 'left' if is_left else 'right'

        player_x, player_y = self.player.rect.center
        target = pygame.Vector2(player_x, player_y - 80)  # posisi target DI ATAS player

        current = pygame.Vector2(hand.rect.center)
        hand.rect.center = current.lerp(target, 0.05)  # smooth movement

        # Serangan jika cukup dekat
        if now - self.cooldowns[side] >= self.cooldown_time[side]:
            if hand.rect.colliderect(self.player.player_hitbox):
                hand.image = self.animations['Handattack1' if is_left else 'Handattack2'][0]
                self.player.take_damage(1)
                self.cooldowns[side] = now
            else:
                hand.image = self.animations['Hand'][0] if is_left else pygame.transform.flip(self.animations['Hand'][0], True, False)


    # ---------------------------- Generic ----------------------------

    def take_damage(self, amount):
        self.hp -= amount
        print(f"Cervus HP: {self.hp}")
        if self.hp <= 0:
            if self.phase == 1:
                self.phase2_setup()
            else:
                self.die()

    def update(self, dt):
        super().animate(dt)

        if self.phase == 1:
            self.move_to_player(dt)
            self.perform_attack()
            self.add_gravity(dt)
        elif self.phase == 2:
            self.status = 'Idle2'  # Pastikan animasi idle tubuh aktif
            self.rect.midbottom = self.deer_hitbox.midbottom  # Pastikan posisi tetap
            self.move_hand(self.left_hand, True, dt)
            self.move_hand(self.right_hand, False, dt)
