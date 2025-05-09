import pygame
from settings import *
from bossbase import BossBase
from noliictu import Noliictu
from os import listdir
from os.path import join, dirname, abspath
from abc import ABC, abstractmethod

# ========================= Sprite Groups =========================
class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2(0, 0)

    #for camera
    def draw(self, target_pos, map_w, map_h):
        self.offset.x = max(min(-(target_pos[0] - WINDOW_WIDTH / 2), 0), WINDOW_WIDTH - map_w)
        self.offset.y = max(min(-(target_pos[1] - WINDOW_HEIGHT / 2), 0), WINDOW_HEIGHT - map_h)

        for sprite in self:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


# ========================= Abstract Entity Class =========================
class Entity(pygame.sprite.Sprite, ABC):
    def __init__(self, groups):
        super().__init__(groups)

    @abstractmethod
    def import_assets(self): pass

    @abstractmethod
    def import_folder(self, path): pass

    @abstractmethod
    def move(self): pass

    @abstractmethod
    def update(self, dt): pass

# ========================= Player Class =========================
class Player(Entity):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.animations = {k: [] for k in ['Idle', 'Move', 'Attack', 'Attack2', 'Jump', 'Fall']}
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 6
        self.state = 'idle'

        self.image = self.animations[self.get_animation_key()][self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)
        self.collision_sprites = collision_sprites
        self.groupss = groups

        # Stats
        #hp-----------
        self.max_hp = 4
        self.hp = self.max_hp
        #stamina---------
        self.max_stamina = 4
        self.stamina = self.max_stamina
        self.stamina_regen = 1
        self.stamina_drain_attack = 0.5
        self.last_stamina_use = pygame.time.get_ticks()
        

        self.invincible = False
        self.invincibility_duration = 1000
        self.last_hit_time = 0

        # Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 200
        self.gravity = 50
        self.jump_speed = -15
        self.jumping = False
        self.facing_right = True

        # Attack
        self.attacking = False
        self.attacking_two = False
        self.attack_locked = False
        self.attack_button_pressed = False
        self.max_combo = 2
        self.current_combo = 1
        self.combo_reset_time = 900
        self.last_attack_time = 0

        self.player_hitbox = pygame.Rect(0, 0, 16, 32)

#-----------------------------------------------Importing thingy-----------------------------------------------
    def import_assets(self):
        base_path = join(dirname(abspath(__file__)), '..', 'Assets', 'Player')
        for action in self.animations:
            full_path = join(base_path, action)
            self.animations[action] = self.import_folder(full_path)

    def import_folder(self, path):
        return [pygame.image.load(join(path, f)).convert_alpha()
                for f in sorted(listdir(path), key=lambda x: int(x.split('.')[0]))]

##-----------------------------------------------Movement-----------------------------------------------
    def jump(self, keys):
        if keys[pygame.K_SPACE] and self.on_ground() and not self.jumping:
            self.direction.y = self.jump_speed
            self.jumping = True

    def move(self):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]

        if self.direction.x != 0:
            self.facing_right = self.direction.x > 0

        self.jump(keys)
        self.attack(mouse_pressed)

#-----------------------------------------------attacking thingy-----------------------------------------------
    def attack(self, mouse_pressed):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.combo_reset_time:
            self.current_combo = 1

        if mouse_pressed[0] and not self.attack_button_pressed:
            self.attack_button_pressed = True
            self.last_attack_time = current_time

            if self.current_combo == 1 and not self.attacking:
                self._start_attack('attack1')
            elif self.current_combo == 2 and not self.attacking_two:
                self._start_attack('attack2')

        elif not mouse_pressed[0]:
            self.attack_button_pressed = False

    def _start_attack(self, state):
        if state in ['attack1', 'attack2']: stamina_cost = self.stamina_drain_attack 
        if self.stamina < stamina_cost:
            print('Not enough stamina!')
            return
        self.stamina -= stamina_cost
        self.last_stamina_use = pygame.time.get_ticks()

        setattr(self, 'attacking' if state == 'attack1' else 'attacking_two', True)
        self.attack_locked = True
        self.frame_index = 0
        self.state = state

        hitbox = self.attack_hitbox()
        for enemy in self.groupss:
            if isinstance(enemy, (Humanoid, Noliictu)):
                target_hitbox = getattr(enemy, 'entity_hitbox', getattr(enemy, 'hitbox', None))
                if target_hitbox and hitbox.colliderect(target_hitbox):
                    damage = 100 if isinstance(enemy, Noliictu) else 1
                    enemy.take_damage(damage)

    def attack_hitbox(self):
        hitbox = self.player_hitbox.copy()
        hitbox.height = 32
        hitbox.width += 25 if self.facing_right else -45
        return hitbox

    def take_damage(self, damage):
        if not self.invincible:
            self.hp -= damage
            print(f"Player terkena damage! HP sekarang: {self.hp}")
            if self.hp <= 0:
                self.die()
            else:
                self.invincible = True
                self.last_hit_time = pygame.time.get_ticks()

    def die(self):
        print("Player mati!")
        self.kill()

#-----------------------------------------------Physics thingy-----------------------------------------------
    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt
        self.player_hitbox.y += self.direction.y
        self.collision('vertical')

        self.player_hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        self.rect.center = self.player_hitbox.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.player_hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.player_hitbox.right = sprite.rect.left
                    elif self.direction.x < 0: self.player_hitbox.left = sprite.rect.right
                elif direction == 'vertical':
                    if self.direction.y > 0:
                        self.player_hitbox.bottom = sprite.rect.top
                        self.direction.y = 0
                        self.jumping = False
                    elif self.direction.y < 0:
                        self.player_hitbox.top = sprite.rect.bottom
                        self.direction.y = 0
        self.rect.center = self.player_hitbox.center

    def on_ground(self):
        self.player_hitbox.y += 1
        grounded = any(sprite.rect.colliderect(self.player_hitbox) for sprite in self.collision_sprites)
        self.player_hitbox.y -= 1
        return grounded

#-----------------------------------------------Animations thingy-----------------------------------------------
    def get_animation_key(self):
        return {
            'idle': 'Idle', 'move': 'Move', 'jump': 'Jump',
            'fall': 'Fall', 'attack1': 'Attack', 'attack2': 'Attack2'
        }[self.state]

    def update_state(self):
        if self.attacking or self.attacking_two:
            return
        if self.direction.y < 0:
            self.state = 'jump'
        elif self.direction.y > 1 and not self.on_ground():
            self.state = 'fall'
        elif self.direction.x != 0:
            self.state = 'move'
        else:
            self.state = 'idle'

    def update_animation(self, dt):
        frames = self.animations[self.get_animation_key()]
        self.frame_index += (8 if 'attack' in self.state else 6) * dt

        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.state == 'attack1':
                self.attacking = False
                self.attack_locked = False
                self.current_combo = 2
                self.state = 'idle'
            elif self.state == 'attack2':
                self.attacking_two = False
                self.attack_locked = False
                self.current_combo = 1
                self.state = 'idle'

        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

#-----------------------------------------------Update-----------------------------------------------
    def update(self, dt):
        self.player_hitbox.center = self.rect.center
        self.move()
        self.add_gravity(dt)
        self.update_state()
        self.update_animation(dt)

        #combo reset
        if pygame.time.get_ticks() - self.last_attack_time > self.combo_reset_time:
            self.current_combo = 1

        #regen stamina
        time_since_use = (pygame.time.get_ticks() - self.last_stamina_use) / 1000
        regen_amount = self.stamina_regen * dt
        # 1 detik
        if time_since_use > 1 and self.stamina < self.max_stamina and not self.attack_button_pressed:
            self.stamina = min(self.stamina + regen_amount, self.max_stamina)

        #playa invicible, utk testing
        if self.invincible and pygame.time.get_ticks() - self.last_hit_time > self.invincibility_duration:
            self.invincible = False

# ========================= Humanoid Class =========================
class Humanoid(Entity):
    def __init__(self, type, pos, groups, collision_sprites):
        super().__init__(groups)
        self.type = type
        self.animations = {k: [] for k in ['Idle', 'Move', 'Attack']}
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 6
        self.state = 'idle'

        self.image = self.animations[self.get_animation_key()][self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)
        self.collision_sprites = collision_sprites

        # Movement
        self.direction = pygame.math.Vector2(-1, 0)
        self.speed = 60
        self.gravity = 50
        self.facing_right = False
        self.left_bound = None
        self.right_bound = None

        # Wandering
        self.wandering = self.type in ['Sword', 'Axe']
        self.wander_timer = 0
        self.wander_duration = 2000
        self.idle_duration = 1000
        self.wander_lap = pygame.time.get_ticks()

        # Combat
        self.attacking = False
        self.entity_hitbox = pygame.Rect(0, 0, 16, 32)

        # Health
        self.hp = {'Sword': 2, 'Spear': 3, 'Axe': 4}.get(self.type, 1)
        self.death_time = 0
        self.death_duration = 400

#-----------------------------------------------Importing thingy-----------------------------------------------
    def import_assets(self):
        base_path = join(dirname(abspath(__file__)), '..', 'Assets', 'Enemy', 'Skelly', self.type)
        for action in self.animations:
            full_path = join(base_path, action)
            self.animations[action] = self.import_folder(full_path)

    def import_folder(self, path):
        return [pygame.image.load(join(path, f)).convert_alpha()
                for f in sorted(listdir(path), key=lambda x: int(x.split('.')[0]))]

#-----------------------------------------------status thingy-----------------------------------------------
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.die()

    def die(self):
        self.death_time = pygame.time.get_ticks()
        mask = pygame.mask.from_surface(self.image)
        surf = mask.to_surface(setcolor=(255, 100, 0), unsetcolor=(0, 0, 0, 0))
        surf.set_colorkey((0, 0, 0))
        self.image = surf
        self.direction = pygame.math.Vector2(0, 0)
        self.attacking = False

#-----------------------------------------------movement thingy-----------------------------------------------
    def move(self, dt):
        now = pygame.time.get_ticks()

        if not self.wandering:
            self.direction.x = 0
            return

        if self.state == 'idle':
            self.direction.x = 0
            if now - self.wander_lap >= self.idle_duration:
                self.state = 'walk'
                self.direction.x = 1 if self.facing_right else -1
                self.wander_lap = now
        elif self.state == 'walk':
            if now - self.wander_lap >= self.wander_duration:
                self.state = 'idle'
                self.wander_lap = now
                self.facing_right = not self.facing_right
            self.direction.x = 1 if self.facing_right else -1

        if self.left_bound is not None and self.right_bound is not None:
            cx = self.entity_hitbox.centerx
            if cx < self.left_bound or cx > self.right_bound:
                if cx <= self.left_bound + 2:
                    self.facing_right = True
                    self.direction.x = 1
                elif cx >= self.right_bound - 2:
                    self.facing_right = False
                    self.direction.x = -1

        self.direction.x = max(-1, min(1, self.direction.x))

    def patrol_bounds(self, rect):
        if rect:
            self.left_bound = rect.left
            self.right_bound = rect.right

#-----------------------------------------------Physics thingy-----------------------------------------------
    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt
        self.entity_hitbox.y += self.direction.y
        self.collision('vertical')

        self.entity_hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        self.rect.center = self.entity_hitbox.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.entity_hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.entity_hitbox.right = sprite.rect.left
                    elif self.direction.x < 0: self.entity_hitbox.left = sprite.rect.right
                elif direction == 'vertical':
                    if self.direction.y > 0:
                        self.entity_hitbox.bottom = sprite.rect.top
                        self.direction.y = 0
                    elif self.direction.y < 0:
                        self.entity_hitbox.top = sprite.rect.bottom
                        self.direction.y = 0
        self.rect.center = self.entity_hitbox.center

#-----------------------------------------------Animations thingy-----------------------------------------------
    def get_animation_key(self):
        return {'idle': 'Idle', 'move': 'Move', 'attack': 'Attack'}[self.state]

    def update_state(self):
        if self.attacking:
            return
        self.state = 'move' if self.direction.x != 0 else 'idle'

    def update_animation(self, dt):
        frames = self.animations[self.get_animation_key()]
        self.frame_index += (8 if 'attack' in self.state else 6) * dt

        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.state == 'attack':
                self.attacking = False
                self.state = 'idle'

        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

#-----------------------------------------------Update-----------------------------------------------
    def update(self, dt):
        now = pygame.time.get_ticks()
        if self.death_time == 0:
            self.entity_hitbox.center = self.rect.center
            self.move(dt)
            self.add_gravity(dt)
            self.update_state()
            self.update_animation(dt)
        elif now - self.death_time >= self.death_duration:
            self.kill()

        