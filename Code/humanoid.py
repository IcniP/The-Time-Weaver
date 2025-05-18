from settings import *
from entity import *

# ========================= Humanoid Class =========================
class Humanoid(Entity):
    def __init__(self, type, pos, groups, collision_sprites):
        super().__init__(groups)
        self.groupss = groups
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
        self.spear_direction = pygame.math.Vector2(0, 0) #agar spear nggk ngikut jalan kalau directionny berubah2
        self.speed = 60
        self.gravity = 50
        self.facing_right = False
        self.left_bound = None
        self.right_bound = None
        self.knockback_timer = 0
        self.knockback_duration = 200

        # Wandering
        self.wandering = self.type in ['Sword', 'Axe']
        self.wander_timer = 0
        self.wander_duration = 2000
        self.idle_duration = 1000
        self.wander_lap = pygame.time.get_ticks()
        self.zone = None

        # Combat
        #attack delay before executing it
        self.attack_windup = 1000  # milliseconds before the attack executes
        self.attack_started_time = 0
        self.attack_ready = False  # set True when wind-up ends
        self.damage_applied = False
        
        #sword n axe
        self.attacking = False
        self.attack_cd = 3000
        self.last_attack_time = 0
        self.entity_hitbox = pygame.Rect(0, 0, 16, 32)

        #spear
        self.thrusting = False
        self.thrusting_distance = TILE_SIZE * 5
        self.thrust_speed = 300
        self.thrust_direction = 0
        self.thrust_progress = 0
        self.thrust_cd = 2000
        self.last_thrust_time = 0

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

        if hasattr(self, 'player_ref'):
            dx = self.entity_hitbox.centerx - self.player_ref.player_hitbox.centerx
            knockback_speed = 100
            knockback_upward = -300

            self.direction.x = 1 if dx > 0 else -1
            self.direction.x *= knockback_speed / self.speed
            self.direction.y = knockback_upward / self.gravity

            self.knockback_timer = pygame.time.get_ticks()

        if self.hp <= 0:
            self.die()

    def die(self, instant = False):
        if instant:
            self.kill()
            return

        self.death_time = pygame.time.get_ticks()
        mask = pygame.mask.from_surface(self.image)
        surf = mask.to_surface(setcolor=(255, 100, 0), unsetcolor=(0, 0, 0, 0))
        surf.set_colorkey((0, 0, 0))
        self.image = surf
        self.direction = pygame.math.Vector2(0, 0)
        self.attacking = False

        if random.randint(1, 100) <= 40:
            KnifeDrop(self.rect.center, self.groupss, self.player_ref)

#-----------------------------------------------movement thingy-----------------------------------------------
    def move(self):
        now = pygame.time.get_ticks()

        if not self.wandering or self.type == 'Spear':
            self.direction.x = 0
            return

        if self.state == 'idle':
            self.direction.x = 0
            if now - self.wander_lap >= self.idle_duration:
                self.state = 'move'
                self.direction.x = 1 if self.facing_right else -1
                self.wander_lap = now
        elif self.state == 'move':
            if now - self.wander_lap >= self.wander_duration:
                self.state = 'idle'
                self.wander_lap = now
                self.facing_right = not self.facing_right
            self.direction.x = 1 if self.facing_right else -1

        if self.left_bound is not None and self.right_bound is not None:
            cx = self.entity_hitbox.centerx
            if cx <= self.left_bound:
                self.facing_right = True
                self.state = 'move'
                self.wander_lap = now
            elif cx >= self.right_bound:
                self.facing_right = False
                self.state = 'move'
                self.wander_lap = now

        self.direction.x = max(-1, min(1, self.direction.x))

    def patrol_bounds(self, rect):
            if rect:
                self.left_bound = rect.left
                self.right_bound = rect.right
                self.zone = rect
    
    def sword_behavior(self):
        if not hasattr(self, 'player_ref'):
            self.move()
            return
        
        player = self.player_ref

        if not self.zone or not self.zone.colliderect(player.player_hitbox):
            self.move()
            return

        px, py = player.player_hitbox.center
        ex, ey = self.entity_hitbox.center

        self.facing_right = px > ex
        offset = 16 if self.facing_right else -32
        attack_hitbox = pygame.Rect(ex + offset, ey - 16, 64, 32)

        if attack_hitbox.collidepoint(px, py):
            dx = px - ex
            self.direction.x = 1 if dx > 5 else -1 if dx < -5 else 0
        
            current_time = pygame.time.get_ticks()
            distance_x = abs(px - ex)

            if distance_x > TILE_SIZE:
                self.direction.x = 1 if px > ex else -1
            else:
                self.direction.x = 0

                if pygame.time.get_ticks() - self.last_attack_time < self.attack_cd:
                    return
                
                if not self.attack_ready:
                    self.attack_started_time = current_time
                    self.attack_ready = True
                    self.state = 'attack'
                    self.damage_applied = False
                    self.frame_index = 0
                    return

                # Delay passed? Then actually attack
                if self.attack_ready and current_time - self.attack_started_time >= self.attack_windup:
                    self.attacking = True
                    self.attack_ready = False
                    self.last_attack_time = current_time
        else:
            self.move()
    
    def axe_behavior(self):
        if not hasattr(self, 'player_ref'):
            self.move()
            return
        
        player = self.player_ref

        if not self.zone or not self.zone.colliderect(player.player_hitbox):
            self.move()
            return

        px, py = player.player_hitbox.center
        ex, ey = self.entity_hitbox.center

        self.facing_right = px > ex
        offset = 16 if self.facing_right else -32
        attack_hitbox = pygame.Rect(ex + offset, ey - 48, 64, 64)

        if attack_hitbox.collidepoint(px, py):
            dx = px - ex
            self.direction.x = 1 if dx > 5 else -1 if dx < -5 else 0
        
            current_time = pygame.time.get_ticks()
            distance_x = abs(px - ex)

            if distance_x > TILE_SIZE:
                self.direction.x = 1 if px > ex else -1
            else:
                self.direction.x = 0

                if pygame.time.get_ticks() - self.last_attack_time < self.attack_cd:
                    return
                    
                if not self.attack_ready:
                    self.attack_started_time = current_time
                    self.attack_ready = True
                    self.state = 'attack'
                    self.damage_applied = False
                    self.frame_index = 0
                    return

                # Delay passed? Then actually attack
                if self.attack_ready and current_time - self.attack_started_time >= self.attack_windup:
                    self.attacking = True
                    self.attack_ready = False
                    self.last_attack_time = current_time
        else:
            self.move()

    def spear_behavior(self, dt):
        if not hasattr(self, 'player_ref'):
            return
        
        if pygame.time.get_ticks() - self.knockback_timer < self.knockback_duration:
            return

        player = self.player_ref
        px, py = player.player_hitbox.center
        ex, ey = self.entity_hitbox.center
        dx = px - ex
        dy = abs(py - ey)
        distance_x = abs(dx)
        now = pygame.time.get_ticks()

        in_range = distance_x <= TILE_SIZE * 5 and dy < TILE_SIZE

        # Always face the player while in range
        if in_range:
            self.facing_right = dx > 0

        # --- Thrusting logic ---
        if self.thrusting:
            move = self.thrust_direction * self.thrust_speed * dt
            self.entity_hitbox.x += move
            self.thrust_progress += abs(move)
            self.rect.center = self.entity_hitbox.center

            # Thrust hitbox
            thrust_hitbox = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
            if self.facing_right:
                thrust_hitbox.midleft = self.entity_hitbox.midright
            else:
                thrust_hitbox.midright = self.entity_hitbox.midleft

            if thrust_hitbox.colliderect(player.player_hitbox) and not player.invincible:
                player.take_damage(1)

            if self.thrust_progress >= self.thrusting_distance:
                self.thrusting = False
                self.state = 'idle'
                self.frame_index = 0
            return

        # --- Windup logic (start only once when player first enters range) ---
        if in_range and not self.attack_ready:
            self.attack_ready = True
            self.attack_started_time = now
            self.state = 'attack'
            self.frame_index = 0

        # --- Do the thrust after 3s passed (even if player left range) ---
        if self.attack_ready and now - self.attack_started_time >= 3000:
            if now - self.last_thrust_time >= self.thrust_cd:
                self.thrusting = True
                self.thrust_progress = 0
                self.thrust_direction = 1 if dx > 0 else -1
                self.facing_right = self.thrust_direction > 0
                self.state = 'attack'
                self.frame_index = 0
                self.last_thrust_time = now
                self.attack_ready = False  # reset windup flag

#-----------------------------------------------Attack---------------------------------
    def attack_hitbox(self):
        hitbox = self.entity_hitbox.copy()
        if self.type == 'Sword':
            # Horizontal slash in front
            hitbox.width = TILE_SIZE  # 32px wide
            if self.facing_right:
                hitbox.left = self.entity_hitbox.right
            else:
                hitbox.right = self.entity_hitbox.left

        elif self.type == 'Axe':
            # Bigger hitbox: wide and tall arc
            hitbox.width = TILE_SIZE
            hitbox.height = TILE_SIZE * 2
            hitbox.top = self.entity_hitbox.top - TILE_SIZE  # reach 1 tile above
            if self.facing_right:
                hitbox.left = self.entity_hitbox.right
            else:
                hitbox.right = self.entity_hitbox.left

        return hitbox

#-----------------------------------------------Physics thingy-----------------------------------------------
    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt
        self.entity_hitbox.y += self.direction.y
        self.collision('vertical')

        if self.type == 'Spear':
            if self.thrusting:
                self.entity_hitbox.x += self.spear_direction.x * self.thrust_speed * dt
            else:
                self.entity_hitbox.x += self.direction.x * self.speed * dt
        else:
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
        if self.attacking or self.thrusting or self.attack_ready:
            return

        if self.type == 'Spear':
            if self.thrusting:
                self.state = 'attack'
            else:
                self.state = 'idle'

    def update_animation(self, dt):
        frames = self.animations[self.get_animation_key()]
        self.frame_index += (8 if 'attack' in self.state else 6) * dt

        if self.state == 'attack' and int(self.frame_index) == 2 and not self.damage_applied:
            hitbox = self.attack_hitbox()
            if hitbox.colliderect(self.player_ref.player_hitbox) and not self.player_ref.invincible:
                self.player_ref.take_damage(1)
            self.damage_applied = True

        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.state == 'attack':
                self.attacking = False
                self.state = 'idle'
                self.last_attack_time = pygame.time.get_ticks()

        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

#-----------------------------------------------Update-----------------------------------------------
    def update(self, dt):
        now = pygame.time.get_ticks()
        if self.death_time == 0:
            self.entity_hitbox.center = self.rect.center

            if now - self.knockback_timer < self.knockback_duration:                
                pass
            else:
                if self.type == 'Sword':
                    self.sword_behavior()
                elif self.type == 'Axe':
                    self.axe_behavior()
                elif self.type == 'Spear':
                    self.spear_behavior(dt)

            if self.type == 'Spear' and not self.thrusting:
                if pygame.time.get_ticks() - self.knockback_timer >= self.knockback_duration:
                    self.direction.x = 0

            self.add_gravity(dt)
            self.update_state()
            self.update_animation(dt)
        elif now - self.death_time >= self.death_duration:
            self.kill()