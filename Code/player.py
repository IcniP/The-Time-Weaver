from settings import *
from entity import *
from noliictu import Noliictu
from bossbase import BossBase

class Player(Entity):
    def __init__(self, pos, groups, collision_sprites, camera_group):
        super().__init__(groups)
        self.animations = {k: [] for k in ['Idle', 'Move', 'Attack', 'Attack2', 'Jump', 'Fall', 'Dash']}
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 6
        self.state = 'idle'

        self.image = self.animations[self.get_animation_key()][self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)
        self.collision_sprites = collision_sprites
        self.groupss = groups
        self.camera_group = camera_group

        # Stats
        #hp-----------
        self.max_hp = 4
        self.hp = self.max_hp
        self.dead = False
        #stamina---------
        self.max_stamina = 4
        self.stamina = self.max_stamina
        self.stamina_regen = 1
        self.last_stamina_use = pygame.time.get_ticks()

        self.invincible = False
        self.invincibility_duration = 1000
        self.last_hit_time = 0

        # Movement---------
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 200
        self.gravity = 30
        self.jump_speed = -11.6
        self.jumping = False
        self.facing_right = True

        #dash---------
        self.can_dash = True
        self.is_dashing = False
        self.air_dash = False
        self.dash_pressed = False
        self.dash_timer = 0
        self.dash_duration = 0.3
        self.dash_speed = 300
        self.dash_cd = 1
        self.time_since_last_dash = 0
        self.attack_cd_after_dash = 500
        self.last_dash_end_time = 0

        # Attack---------
        self.attacking = False
        self.attacking_two = False
        self.attack_locked = False
        self.attack_button_pressed = False
        self.max_combo = 2
        self.current_combo = 1
        self.combo_reset_time = 900
        self.last_attack_time = 0

        #throwing knife attack----------
        self.throw_hand = self.import_folder('Assets/Player/Throw/hand')
        self.throw_body = self.import_folder('Assets/Player/Throw/base')
        self.throw_frame_index = 0
        self.throwing = False
        self.throw_direction = pygame.Vector2(1, 0)
        self.knives = 4
        self.max_knives = 4



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
    
    def dash(self, keys, dt):
        self.time_since_last_dash += dt
        stamina_cost = 1

        if keys[pygame.K_LSHIFT] and not self.dash_pressed and not self.is_dashing and not self.attack_locked:
            
            if self.stamina < stamina_cost:
                return

            if self.on_ground() or not self.air_dash:
                self.is_dashing = True
                self.dash_timer = 0
                self.frame_index = 0
                self.state = 'dash'
                self.attack_locked = True
                self.dash_pressed = True
                self.invincible = True

                self.stamina -= stamina_cost
                self.last_stamina_use = pygame.time.get_ticks()

                if not self.on_ground():
                    self.air_dash = True  # mark dashed in air

        if not keys[pygame.K_LSHIFT]:
            self.dash_pressed = False

        # Dash movement
        if self.is_dashing:
            self.dash_timer += dt
            dash_dir = 1 if self.facing_right else -1
            self.player_hitbox.x += dash_dir * self.dash_speed * dt

            if self.dash_timer >= self.dash_duration:
                self.is_dashing = False
                self.invincible = False
                self.attack_locked = False
                self.last_dash_end_time = pygame.time.get_ticks()
                self.state = 'idle'

        # Reset air dash when grounded
        if self.on_ground():
            self.air_dash = False

    def move(self, dt):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]

        if self.direction.x != 0:
            self.facing_right = self.direction.x > 0

        self.dash(keys, dt)
        self.jump(keys)
        self.attack(mouse_pressed)
        self.throw_knife(mouse_pressed)

#-----------------------------------------------attacking thingy-----------------------------------------------
    def attack(self, mouse_pressed):
        current_time = pygame.time.get_ticks()

        #biar nggk bisa attack klo pas nge dash sma cd setelah dashny blm brakhir
        if self.is_dashing or current_time - self.last_dash_end_time < self.attack_cd_after_dash:
            return

        if current_time - self.last_attack_time > self.combo_reset_time:
            self.current_combo = 1

        if mouse_pressed[0] and not self.attack_button_pressed:
            self.attack_button_pressed = True
            self.last_attack_time = current_time

            if self.current_combo == 1 and not self.attacking:
                self.start_attack('attack1')
            elif self.current_combo == 2 and not self.attacking_two:
                self.start_attack('attack2')

        elif not mouse_pressed[0]:
            self.attack_button_pressed = False

    def start_attack(self, state):
        stamina_cost = 0.5

        if self.stamina < stamina_cost:
            return

        self.stamina -= stamina_cost
        self.last_stamina_use = pygame.time.get_ticks()

        setattr(self, 'attacking' if state == 'attack1' else 'attacking_two', True)
        self.attack_locked = True
        self.frame_index = 0
        self.state = state

        hitbox = self.attack_hitbox()
        for enemy in self.groupss:
            if isinstance(enemy, (Entity)):
                target_hitbox = getattr(enemy, 'entity_hitbox', getattr(enemy, 'hitbox', None))
                if target_hitbox and hitbox.colliderect(target_hitbox):
                    damage = 100 if isinstance(enemy, Noliictu) else 1
                    enemy.take_damage(damage)

    def attack_hitbox(self):
        hitbox = self.player_hitbox.copy()
        hitbox.height = 32
        hitbox.width += 25 if self.facing_right else -45
        return hitbox
    
    def throw_knife(self, mouse_pressed):
         if self.knives != 0:
            if mouse_pressed[2] and not self.throwing:
                self.throwing = True
                self.throw_frame_index = 0
                self.attack_locked = True

                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

                player_screen_pos = pygame.Vector2(self.rect.center) + self.camera_group.offset

                self.throw_direction = (mouse_pos - player_screen_pos).normalize()
                self.facing_right = self.throw_direction.x >= 0

                world_mouse = self.rect.center + (mouse_pos - player_screen_pos)

                enemies = [s for s in self.groupss if isinstance(s, (Entity))]
                PlayerKnife(self.rect.center, world_mouse, self.groupss, enemies)
                self.knives -= 1

    def take_damage(self, damage):
        if  self.invincible == False:
            self.hp -= damage
            self.invincible = True
            self.last_hit_time = pygame.time.get_ticks()
            print(f"Player terkena damage! HP sekarang: {self.hp}")
            if self.hp <= 0:
                self.die()
                

    def die(self):
        if not self.dead:
            self.dead = True
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
            'idle': 'Idle', 
            'move': 'Move', 
            'jump': 'Jump',
            'fall': 'Fall', 
            'attack1': 'Attack', 
            'attack2': 'Attack2', 
            'dash': 'Dash'
        }[self.state]

    def update_state(self):
        if self.attacking or self.attacking_two or self.is_dashing:
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
        if self.throwing:
            self.throw_frame_index += 8 * dt
            if self.throw_frame_index >= len(self.throw_hand):
                self.throw_frame_index = 0
                self.throwing = False
                self.hand_image = None
                self.state = 'idle'
                self.attack_locked = False
                return

            self.image = self.throw_body[int(self.throw_frame_index)]
            self.hand_image = self.throw_hand[int(self.throw_frame_index)]

            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
                self.hand_image = pygame.transform.flip(self.hand_image, True, False)
            return  # skip rest while throwing



        frames = self.animations[self.get_animation_key()]
        self.frame_index += (8 if 'attack' in self.state or self.state == 'Dash' else 6) * dt

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
            elif self.state == 'dash':
                self.is_dashing = False
                self.attack_locked = False
                self.state = 'idle'
        
        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

#-----------------------------------------------Update-----------------------------------------------
    def update(self, dt):
        self.player_hitbox.center = self.rect.center
        self.move(dt)
        self.add_gravity(dt)
        self.update_state()
        self.update_animation(dt)

        #combo reset-------------
        if pygame.time.get_ticks() - self.last_attack_time > self.combo_reset_time:
            self.current_combo = 1

        #regen stamina-----------
        time_since_use = (pygame.time.get_ticks() - self.last_stamina_use) / 1000
        regen_amount = self.stamina_regen * dt
        # 1 detik
        if time_since_use > 1 and self.stamina < self.max_stamina and not self.attack_button_pressed and not self.jumping and not self.is_dashing:
            self.stamina = min(self.stamina + regen_amount, self.max_stamina)

        #playa invicible, utk testing----------
        if self.invincible and pygame.time.get_ticks() - self.last_hit_time > self.invincibility_duration:
            self.invincible = False


class PlayerKnife(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos, groups, enemies):
        super().__init__(groups)
        self.image_original = pygame.image.load(join('Assets', 'Player', 'Throw', 'knife', '0.png')).convert_alpha()

        self.start_pos = pygame.Vector2(pos)
        direction_vector = pygame.Vector2(target_pos) - self.start_pos
        self.direction = direction_vector.normalize() if direction_vector.length() > 0 else pygame.Vector2(1, 0)

        angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(self.image_original, -angle)
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 600
        self.range = 1000
        self.enemies = enemies  # Sprite group to collide with
        self.damage = 1

    def update(self, dt):
        move = self.direction * self.speed * dt
        self.rect.centerx += move.x
        self.rect.centery += move.y

        current_pos = pygame.Vector2(self.rect.center)
        if self.start_pos.distance_to(current_pos) >= self.range:
            self.kill()
            return

        for enemy in self.enemies:
            target_hitbox = getattr(enemy, 'entity_hitbox', getattr(enemy, 'hitbox', None))
            if target_hitbox and self.rect.colliderect(target_hitbox):
                if isinstance(enemy, Noliictu):
                    enemy.take_damage(100)
                else:
                    enemy.take_damage(self.damage)
                self.kill()
                return