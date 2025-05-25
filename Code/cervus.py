import pygame
from settings import *
from bossbase import BossBase

class Cervus(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, collision_sprites=None):
        super().__init__(groups)
        self.phase = 1
        self.groups = groups
        self.player = player
        self.collision_sprites = collision_sprites

        spawn_pos = (player.rect.centerx, player.rect.top - 96)
        self.current_phase = CervusPhase1(spawn_pos, groups, player, collision_sprites)

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

    def __getattr__(self, attr):
        return getattr(self.current_phase, attr)


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
        self.speed = 60
        self.gravity = 30
        self.direction = pygame.Vector2(0, 0)
        self.jumping = False
        self.cooldowns = {'stomp': 0, 'dash': 0}
        self.cooldown_time = {'stomp': 10000, 'dash': 15000}
        self.attack_in_progress = False
        self.attack_end_time = 0

        self.deer_hitbox = pygame.Rect(0, 0, 32, 32)
        self.deer_hitbox.midbottom = self.rect.midbottom
        self.entity_hitbox = self.deer_hitbox.inflate(20, 0)

    def move(self, dt):
        self.rect.center = self.deer_hitbox.center
        px = self.player.rect.centerx
        ex = self.rect.centerx
        self.direction.x = 1 if px > ex else -1 if px < ex else 0

        self.deer_hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.rect.center = self.deer_hitbox.center

        if not self.attack_in_progress:
            self.status = 'Deerwalk' if self.direction.x != 0 else 'Deeridle'
        self.facing_right = self.direction.x > 0

    def perform_attack(self):
        if self.hp <= 0: return
        now = pygame.time.get_ticks()
        if self.attack_in_progress and now >= self.attack_end_time:
            self.attack_in_progress = False
            return

        if not self.attack_in_progress:
            if now - self.cooldowns['stomp'] >= self.cooldown_time['stomp']:
                self.play_animation('Deerstomp')
                self.cooldowns['stomp'] = now
                self.attack_in_progress = True
                self.attack_end_time = now + 800
                self.damage_player()
            elif now - self.cooldowns['dash'] >= self.cooldown_time['dash']:
                self.play_animation('Deerdash')
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
        self.rect.center = self.deer_hitbox.center
        self.entity_hitbox.center = self.deer_hitbox.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.deer_hitbox):
                if direction == 'horizontal':
                    self.deer_hitbox.right = sprite.rect.left if self.direction.x > 0 else self.deer_hitbox.left
                    self.direction.x = 0
                elif direction == 'vertical':
                    self.deer_hitbox.bottom = sprite.rect.top if self.direction.y > 0 else self.deer_hitbox.bottom
                    self.direction.y = 0

    def update(self, dt):
        self.animate(dt)
        self.perform_attack()
        self.move(dt)
        self.add_gravity(dt)

class CervusPhase2:
    def __init__(self, pos, groups, player):
        self.hp = 800
        self.player = player
        self.groups = groups

        animation_paths = {
            'Idle2': ['cervus', '1st'],
            'Hand': ['cervus', 'hand', 'idle'],
            'Handattack1': ['cervus', 'hand', 'a1'],
            'Handattack2': ['cervus', 'hand', 'a2']
        }

        self.animations = {k: [pygame.image.load(join('Assets', 'Enemy', *v, f)).convert_alpha()
                               for f in sorted(listdir(join('Assets', 'Enemy', *v)), key=lambda x: int(x.split('.')[0]))]
                           for k, v in animation_paths.items()}

        #main body
        map_center_x = player.game.map_w // 2
        map_bottom_y = player.rect.bottom
        center_pos = (map_center_x, map_bottom_y)
        self.main_body = MainBody(center_pos, player, self.animations['Idle2'][0])
        self.left_hand = Hand(pos, player, True, self.main_body, self.animations)
        self.right_hand = Hand(pos, player, False, self.main_body, self.animations)

        groups.add(self.left_hand)
        groups.add(self.right_hand)
        groups.add(self.main_body)

    def update(self, dt):
        self.main_body.update(dt)
        self.left_hand.update(dt)
        self.right_hand.update(dt)

        if self.main_body.hp <= 0:
            self.main_body.kill()
            self.left_hand.kill()
            self.right_hand.kill()


class MainBody(pygame.sprite.Sprite):
    def __init__(self, pos, player, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(pos[0], pos[1] - -90))
        self.entity_hitbox = self.rect.inflate(-30, -30)
        self.player = player
        self.hp = 800
        self.last_hit_time = 0
        self.hit_cooldown = 300

    def take_damage(self, damage):
        now = pygame.time.get_ticks()
        if now - self.last_hit_time > self.hit_cooldown:
            self.hp -= damage
            self.last_hit_time = now
            print("Main body hit! HP:", self.hp)

    def update(self, dt):
        self.entity_hitbox.center = self.rect.center
        if (self.player.attacking or self.player.attacking_two) and self.player.attack_hitbox().colliderect(self.entity_hitbox):
            facing_right = self.player.facing_right
            if (facing_right and self.rect.centerx > self.player.rect.centerx) or \
               (not facing_right and self.rect.centerx < self.player.rect.centerx):
                self.take_damage(1)
        if self.entity_hitbox.colliderect(self.player.player_hitbox):
            if not self.player.invincible:
                self.player.take_damage(1)


class Hand(pygame.sprite.Sprite):
    def __init__(self, pos, player, is_left, anchor, animations):
        super().__init__()
        self.animations = animations
        self.anim_frames = animations['Hand']
        self.frame_index = 0
        self.image = self.anim_frames[0]
        self.rect = self.image.get_rect(center=(pos[0] + (-60 if is_left else 60), pos[1] - 100))
        self.player = player
        self.is_left = is_left
        self.anchor = anchor
        self.attack_timer = 0
        self.attack_type = None

    def start_attack1(self):
        self.anim_frames = self.animations['Handattack1']
        self.frame_index = 0
        self.attack_type = 'stomp'

    def start_attack2(self):
        self.anim_frames = self.animations['Handattack2']
        self.frame_index = 0
        self.attack_type = 'swipe'

    def update(self, dt):
        self.frame_index += 6 * dt
        if self.frame_index >= len(self.anim_frames):
            self.anim_frames = self.animations['Hand']
            self.frame_index = 0
            self.attack_type = None

        self.image = self.anim_frames[int(self.frame_index)]
        target_x = self.player.player_hitbox.centerx
        if self.attack_type == 'stomp':
            target_y = self.player.player_hitbox.bottom + 10
        elif self.attack_type == 'swipe':
            target_y = self.player.player_hitbox.centery
        else:
            target_y = self.player.player_hitbox.top - 50

        if self.is_left and target_x > self.anchor.rect.centerx: return
        if not self.is_left and target_x < self.anchor.rect.centerx: return

        target = pygame.Vector2(target_x, target_y)
        self.rect.center = pygame.Vector2(self.rect.center).lerp(target, 0.1)

        if self.rect.colliderect(self.player.player_hitbox) and not self.player.invincible:
            self.player.take_damage(1)
