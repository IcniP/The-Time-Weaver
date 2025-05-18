import pygame
from settings import *
from bossbase import BossBase

# ============================ WRAPPER ============================
class Cervus(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, collision_sprites=None):
        super().__init__(groups)
        self.phase = 1
        self.groups = groups
        self.player = player
        self.collision_sprites = collision_sprites

        # Spawn Phase 1 dulu
        self.current_phase = CervusPhase1(pos, groups, player, collision_sprites)
    
    def move(self):
        pass

    def update(self, dt):
        self.current_phase.update(dt)

        if self.current_phase.hp <= 0:
            self.next_phase()

    def next_phase(self):
        old_pos = self.current_phase.rect.midbottom
        self.current_phase.kill()

        if self.phase == 1:
            self.phase = 2
            self.current_phase = CervusPhase2(old_pos, self.groups, self.player)
        elif self.phase == 2:
            self.phase = 3
            self.current_phase = CervusPhase3(old_pos, self.groups, self.player)


# ============================ PHASE 1 ============================
class CervusPhase1(BossBase):
    def __init__(self, pos, groups, player, collision_sprites):
        animation_paths = {
            'Deeridle': ['cervus', 'deer', 'idle'],
            'Deerwalk': ['cervus', 'deer', 'walk'],
            'Deerstomp': ['cervus', 'deer', 'stomp'],
            'Deerdash': ['cervus', 'deer', 'dash'],
        }
        super().__init__(pos, groups, player, 'CervusPhase1', animation_paths)
        self.collision_sprites = collision_sprites or pygame.sprite.Group()
        self.hp = 5
        self.phase = 1
        self.speed = 40
        self.gravity = 30
        self.direction = pygame.Vector2(0, 0)
        self.jumping = False
        self.cooldowns = {'stomp': 0, 'dash': 0}
        self.cooldown_time = {'stomp': 30000, 'dash': 15000}
        self.attack_in_progress = False
        self.attack_end_time = 0

        self.deer_hitbox = pygame.Rect(0, 0, 32, 32)
        self.deer_hitbox.midbottom = self.rect.midbottom
        self.entity_hitbox = self.deer_hitbox.inflate(20, 0)
    
    def move(self):
        pass

    def update(self, dt):
        self.animate(dt)
        self.move_to_player(dt)
        self.perform_attack()
        self.add_gravity(dt)

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
        if self.hp <= 0:
            return
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

    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt
        self.deer_hitbox.y += self.direction.y
        self.collision('vertical')
        self.deer_hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.rect.center = self.deer_hitbox.center
        self.entity_hitbox.center = self.deer_hitbox.center

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


# ============================ PHASE 2 ============================
class CervusPhase2(BossBase):
    def __init__(self, pos, groups, player):
        animation_paths = {
            'Idle2': ['cervus', '2nd'],
            'Hand': ['cervus', 'hand', 'idle'],
            'Handattack1': ['cervus', 'hand', 'a1'],
            'Handattack2': ['cervus', 'hand', 'a2']
        }
        super().__init__(pos, groups, player, 'CervusPhase2', animation_paths)
        self.hp = 800
        self.phase = 2
        self.gravity = 0

        # Tangan
        self.left_hand = pygame.sprite.Sprite()
        self.right_hand = pygame.sprite.Sprite()
        self.left_hand.image = pygame.transform.scale2x(self.animations['Hand'][0])
        self.right_hand.image = pygame.transform.scale2x(pygame.transform.flip(self.animations['Hand'][0], True, False))
        offset = 100
        self.left_hand.rect = self.left_hand.image.get_rect(center=(self.rect.centerx - offset, self.rect.centery))
        self.right_hand.rect = self.right_hand.image.get_rect(center=(self.rect.centerx + offset, self.rect.centery))
        self.left_hand.add(*groups) if isinstance(groups, (list, tuple)) else self.left_hand.add(groups)
        self.right_hand.add(*groups) if isinstance(groups, (list, tuple)) else self.right_hand.add(groups)

        self.cooldowns = {'left': 0, 'right': 0}
        self.cooldown_time = {'left': 3000, 'right': 3000}

    def move(self):
        pass

    def update(self, dt):
        self.animate(dt)
        self.move_hand(self.left_hand, True, dt)
        self.move_hand(self.right_hand, False, dt)

    def move_hand(self, hand, is_left, dt):
        now = pygame.time.get_ticks()
        side = 'left' if is_left else 'right'

        player_x, player_y = self.player.rect.center
        target = pygame.Vector2(player_x, player_y - 80)
        current = pygame.Vector2(hand.rect.center)
        hand.rect.center = current.lerp(target, 0.05)

        if now - self.cooldowns[side] >= self.cooldown_time[side]:
            if hand.rect.colliderect(self.player.player_hitbox):
                if is_left:
                    hand.image = pygame.transform.scale2x(self.animations['Handattack1'][0])
                else:
                    hand.image = pygame.transform.scale2x(pygame.transform.flip(self.animations['Handattack2'][0], True, False))
                self.player.take_damage(1)
                self.cooldowns[side] = now
            else:
                if is_left:
                    hand.image = pygame.transform.scale2x(self.animations['Hand'][0])
                else:
                    hand.image = pygame.transform.scale2x(pygame.transform.flip(self.animations['Hand'][0], True, False))


# ============================ PHASE 3 ============================
class CervusPhase3(BossBase):
    def __init__(self, pos, groups, player):
        animation_paths = {
            'Idle3': ['cervus', '3rd']  # jika ada
        }
        super().__init__(pos, groups, player, 'CervusPhase3', animation_paths)
        self.hp = 1000
        self.phase = 3

    def move(self):
        pass

    def update(self, dt):
        pass