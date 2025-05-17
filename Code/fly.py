from settings import *
from entity import *

class Fly(Entity):
    def __init__(self, pos, groups, collision_sprites, player, range_rect = None):
        super().__init__(groups)
        self.start_pos = pygame.Vector2(pos)
        self.range_rect = range_rect
        self.player = player
        self.collision_sprites = collision_sprites

        self.animations = {k: [] for k in ['fly', 'attack']}
        self.state = 'fly'
        self.frame_index = 0
        self.animation_speed = 6

        self.import_assets()
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)
        self.direction = pygame.Vector2(1, 0)
        self.speed = 100
        self.facing_right = True

        # Wander bounds
        self.left_bound = self.start_pos.x - TILE_SIZE * 4
        self.right_bound = self.start_pos.x + TILE_SIZE * 4

        # Attack
        self.attack_cd = 3000  # ms
        self.last_attack_time = 0
        self.projectiles = groups  # will spawn projectiles into AllSprites

        self.entity_hitbox = pygame.Rect(0, 0, 32, 32)

        self.hp = 1
        self.death_time = 0
        self.death_duration = 400
    
    def import_assets(self):
        base_path = join(dirname(abspath(__file__)), '..', 'Assets', 'Enemy', 'Wraith')
        for action in self.animations:
            full_path = join(base_path, action)
            self.animations[action] = self.import_folder(full_path)

    def import_folder(self, path):
        return [pygame.image.load(join(path, f)).convert_alpha()
                for f in sorted(listdir(path), key=lambda x: int(x.split('.')[0]))]
    
    def get_range_zone(self, pos):
        for rect in getattr(self, 'player', None).collision_sprites:
            if hasattr(rect, 'name') and rect.name == 'range':
                if rect.rect.collidepoint(pos):
                    return rect.rect
        return None

    def take_damage(self, damage):
        self.hp -= damage

        if hasattr(self, 'player_ref'):
            dx = self.entity_hitbox.centerx - self.player_ref.player_hitbox.centerx
            self.direction.x = 1 if dx > 0 else -1

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

    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt

        if self.rect.centerx < self.left_bound:
            self.rect.centerx = self.left_bound
            self.direction.x = 1
        elif self.rect.centerx > self.right_bound:
            self.rect.centerx = self.right_bound
            self.direction.x = -1

        self.facing_right = self.direction.x < 0
    
    def can_attack(self):
        if self.range_rect and not self.range_rect.colliderect(self.player.player_hitbox):
            return False
        
        now = pygame.time.get_ticks()
        if now - self.last_attack_time > self.attack_cd:
            self.last_attack_time = now
            return True
        return False

    def shoot(self):
        projectile = Projectile(self.rect.center, self.player.player_hitbox.center, self.projectiles, self.player, self.collision_sprites)
        self.projectiles.add(projectile)

        self.state = 'attack'
        self.frame_index = 0

    def update_animation(self, dt):
        frames = self.animations[self.state]
        self.frame_index += self.animation_speed * dt

        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.state == 'attack':
                self.state = 'fly'

        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, dt):
        now = pygame.time.get_ticks()

        if self.death_time == 0:
            self.entity_hitbox.center = self.rect.center
            self.move(dt)
            if self.can_attack():
                self.shoot()
            self.update_animation(dt)
        elif now - self.death_time >= self.death_duration:
            self.kill()


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player
        self.collision_sprites = collision_sprites

        # Base image
        base_image = pygame.image.load(join('Assets', 'Enemy', 'Wraith', 'projectile', '0.png')).convert_alpha()
        self.original_image = base_image

        # Direction setup
        self.pos = pygame.Vector2(pos)
        direction_vector = pygame.Vector2(target_pos) - self.pos
        self.direction = direction_vector.normalize() if direction_vector.length() > 0 else pygame.Vector2(1, 0)

        # Rotate the image to face direction where playa is
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) + 180
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect()

        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 200
        self.range = 800
        self.start_pos = self.pos.copy()
        self.damage = 1

    def update(self, dt):
        move = self.direction * self.speed * dt
        self.pos += move
        self.rect.midleft = self.pos

        # Range check
        if self.start_pos.distance_to(self.pos) > self.range:
            self.kill()
            return

        # Hit player
        if pygame.sprite.collide_mask(self, self.player):
            self.player.take_damage(self.damage)
            self.kill()
            return

        # Hit ground
        for sprite in self.collision_sprites:
            if self.rect.colliderect(sprite.rect):
                self.kill()
                return