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
    
    def __getattr__(self, attr):
        return getattr(self.current_phase, attr)



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
        self.speed = 10
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
    
    def update(self, dt):
        self.animate(dt)
        self.perform_attack()
        self.move(dt)
        self.add_gravity(dt)

    def move(self, dt):
        if abs(self.player.rect.centerx - self.rect.centerx) > 10:
            self.direction.x = 1 if self.player.rect.centerx > self.rect.centerx else -1
        else:
            self.direction.x = 0

        self.deer_hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.rect.center = self.deer_hitbox.center
        self.status = 'Deerwalk' if self.direction.x != 0 else 'Deeridle'
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
            self.player.take_damage(0) # damage ke player

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
            'Idle2': ['cervus', '1st'],
            'Hand': ['cervus', 'hand', 'idle'],
            'Handattack1': ['cervus', 'hand', 'a2'],  # swipe
            'Handattack2': ['cervus', 'hand', 'a1']   # plunge
        }
        super().__init__(pos, groups, player, 'CervusPhase2', animation_paths)
        self.hp = 800
        self.phase = 2
        self.gravity = 0
        self.sprite_groups = groups

        # Setup hand offset
        offset_x = 50
        offset_y = -120

        # LEFT HAND
        self.left_hand = pygame.sprite.Sprite()
        self.left_hand.image = pygame.transform.scale2x(self.animations['Hand'][0])
        self.left_hand.rect = self.left_hand.image.get_rect(center=(self.rect.centerx - offset_x, self.rect.centery + offset_y))
        self.left_hand.start_pos = self.left_hand.rect.center

        # RIGHT HAND
        self.right_hand = pygame.sprite.Sprite()
        self.right_hand.image = pygame.transform.scale2x(pygame.transform.flip(self.animations['Hand'][0], True, False))
        self.right_hand.rect = self.right_hand.image.get_rect(center=(self.rect.centerx + offset_x, self.rect.centery + offset_y))
        self.right_hand.start_pos = self.right_hand.rect.center

        if isinstance(groups, (list, tuple)):
            for group in groups:
                group.add(self.left_hand)
                group.add(self.right_hand)
        else:
            groups.add(self.left_hand)
            groups.add(self.right_hand)

        self.cooldowns = {
            'left_swipe': 0, 'right_swipe': 0,
            'left_plunge': 0, 'right_plunge': 0
        }
        self.cooldown_time = {
            'left_swipe': 5000, 'right_swipe': 5000,
            'left_plunge': 8000, 'right_plunge': 8000
        }

    def move(self):
        pass

    def create_hand(self, is_left):
        hand = pygame.sprite.Sprite()
        img = self.animations['Hand'][0]
        if not is_left:
            img = pygame.transform.flip(img, True, False)
        hand.image = pygame.transform.scale2x(img)

        offset = -self.default_offset if is_left else self.default_offset
        hand.rect = hand.image.get_rect(center=(self.rect.centerx + offset, self.rect.centery))
        hand.start_pos = pygame.Vector2(hand.rect.center)

    
        if isinstance(self.sprite_groups, (list, tuple)):
            for group in self.sprite_groups:
                group.add(hand)
        else:
            self.sprite_groups.add(hand)

        return hand

    def update(self, dt):
        self.animate(dt)
        self.update_hand(self.left_hand, is_left=True, dt=dt)
        self.update_hand(self.right_hand, is_left=False, dt=dt)

    def update_hand(self, hand, is_left, dt):
        now = pygame.time.get_ticks()
        side = 'left' if is_left else 'right'
        attack_key = f'{side}_swipe'

        player_x = self.player.rect.centerx
        boss_x = self.rect.centerx
        current = pygame.Vector2(hand.rect.center)

        if not hasattr(hand, 'idle_pos'):
            offset_x = -40 if is_left else 40
            offset_y = -100
            hand.idle_pos = pygame.Vector2(self.rect.centerx + offset_x, self.rect.centery + offset_y)

        if (is_left and player_x < boss_x) or (not is_left and player_x > boss_x):
            target = pygame.Vector2(self.player.rect.centerx, self.player.rect.top - 80)
            hand.rect.center = current.lerp(target, 0.05)
        else:
            hand.rect.center = current.lerp(hand.idle_pos, 0.05)

        if now - self.cooldowns[attack_key] >= self.cooldown_time[attack_key]:
            if hand.rect.colliderect(self.player.player_hitbox):
                img = self.animations['Handattack1'][0] if is_left else self.animations['Handattack2'][0]
                if not is_left:
                    img = pygame.transform.flip(img, True, False)
                hand.image = pygame.transform.scale2x(img)
                self.cooldowns[attack_key] = now
            else:
                img = self.animations['Hand'][0]
                if not is_left:
                    img = pygame.transform.flip(img, True, False)
                hand.image = pygame.transform.scale2x(img)



# ============================ PHASE 3 ============================
class CervusPhase3(BossBase):
    def __init__(self, pos, groups, player):
        animation_paths = {
            'Idle3': ['cervus', '2nd']
        }
        super().__init__(pos, groups, player, 'CervusPhase3', animation_paths)
        self.hp = 1000
        self.phase = 3

    def move(self):
        pass

    def update(self, dt):
        pass