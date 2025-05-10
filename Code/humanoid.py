from settings import *
from entity import *

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