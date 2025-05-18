import pygame
from settings import *
from entity import *
from player import *
from bossbase import BossBase

class Knive(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos, groups, player):
        super().__init__(groups)

        num = random.randint(0, 3)
        original_image = pygame.image.load(join('Assets', 'Enemy', 'noliictu', 'Knive', f'{num}.png')).convert_alpha()

        self.start_pos = pygame.math.Vector2(pos)
        self.player = player

        direction_vector = pygame.math.Vector2(target_pos) - self.start_pos
        self.direction = direction_vector.normalize()

        angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(original_image, -angle)
        self.rect = self.image.get_rect(center=pos)

        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 520 #projectile speed
        self.damage = 1  # Damage ke player

    def update(self, dt):
        move = self.direction * self.speed * dt
        self.rect.centerx += move.x
        self.rect.centery += move.y

        # Cek jarak
        current_pos = pygame.math.Vector2(self.rect.center)
        if self.start_pos.distance_to(current_pos) >= 1000:
            self.kill()
            return

        if pygame.sprite.collide_mask(self, self.player):
            self.player.take_damage(self.damage)
            self.kill()

class RainKnive(pygame.sprite.Sprite):
    def __init__(self, groups, player):
        super().__init__(groups)

        num = random.randint(0, 3)
        original_image = pygame.image.load(join('Assets', 'Enemy', 'noliictu', 'Knive', f'{num}.png')).convert_alpha()
        self.image = original_image
        self.image = pygame.transform.rotate(original_image, -90)
        self.rect = self.image.get_rect(midtop=(random.randint(0, 1900), -50))
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 400  # kecepatan jatuh
        self.player = player
        self.damage = 1

    def update(self, dt):
        self.rect.y += self.speed * dt

        if self.rect.top > 2000:
            self.kill()
            return

        if pygame.sprite.collide_mask(self, self.player):
            self.player.take_damage(self.damage)
            self.kill()

class ArcSwordFollow(pygame.sprite.Sprite):
    def __init__(self, player, pos, groups):
        super().__init__(groups)

        num = random.randint(0, 3)
        self.image_original = pygame.image.load(join('Assets', 'Enemy', 'noliictu', 'Knive', f'{num}.png')).convert_alpha()
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=pos)
        self.player = player
        self.offset = pygame.math.Vector2(pos) - pygame.math.Vector2(player.rect.center)

        self.mask = pygame.mask.from_surface(self.image)
        self.follow_player = True
        self.speed = 500
        self.damage = 1
        self.direction = pygame.Vector2(0, 0)

    def update_follow(self):
        self.rect.center = self.player.rect.center + self.offset

    def shoot_towards_player(self):
        self.follow_player = False
        direction_vector = pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.rect.center)
        if direction_vector.length() != 0:
            self.direction = direction_vector.normalize()
        else:
            self.direction = pygame.Vector2(0, 1)

    def update(self, dt):
        if not self.follow_player:
            move = self.direction * self.speed * dt
            self.rect.centerx += move.x
            self.rect.centery += move.y

            if pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(self.player.rect.center)) >= 1000:
                self.kill()

            if pygame.sprite.collide_mask(self, self.player):
                self.player.take_damage(self.damage)
                self.kill()

class Noliictu(BossBase):
    def __init__(self, pos, groups, player):
        animation_paths = {
            'Idle': ['noliictu', 'Idle'],
            'Attack': ['noliictu', 'Attack'],
            'Knive': ['noliictu', 'Knive'],
            'TeleportIn': ['noliictu', 'TeleportIn'],
            'TeleportOut': ['noliictu', 'TeleportOut'],
            'Ult': ['noliictu', 'Ult'],
            'UltIn': ['noliictu', 'UltIn']
        }
        super().__init__(pos, groups, player, boss_name='Noliictu', animation_paths=animation_paths)

        self.hitwidth = 16
        self.hitheight = 32
        self.hitbox = pygame.Rect(0, 0, self.hitwidth, self.hitheight)
        self.image = self.animations['Idle'][0]  
        self.rect = self.image.get_rect(center=pos)
        self.hitbox.center = self.rect.center

        self.hp = 3000
        self.detection_rect = pygame.Rect(self.rect.centerx - 100, self.rect.centery - 100, 200, 200)
        self.detection_active = False
        self.time_in_rect = 0
        self.teleporting = False
        self.teleport_cooldown = 5
        self.ready_to_teleport = False
        self.dying = False

        self.knive_group = groups  

        # attack attributes
        self.attack_cooldown = 5
        self.attack_cooldown_timer = 0
        self.knife_timer = 0
        self.knives_fired = 0
        self.max_knives = 5
        self.knife_interval = 0.5  
        self.attacking = False

        # ult attributes
        self.can_ult = False
        self.ult_cooldown = 40
        self.ult_cooldown_timer = 0
        self.is_uliting = False
        self.ult_duration = 10
        self.ult_timer = 0
        self.after_ult_teleport = False
        self.num = random.randint(1, 9)
        self.recovering_after_ult = False
        self.ult_knives_group = groups  
        self.ult_spawn_timer = 0
        self.ult_spawn_interval = 0.1

        self.after_ult_teleport = False
        #second attacko
        self.arc_cooldown = 15
        self.arc_cooldown_timer = 0
        self.arc_swords = []
        self.arc_ready_to_shoot = False
        self.arc_shoot_timer = 0 
        self.arc_shoot_delay = 0.8  
        self.arc_sword_index_list = []

    def move(self):
        pass

    def spawn_arc_swords(self):
        self.arc_swords.clear()
        self.arc_ready_to_shoot = False
        self.arc_shoot_timer = 0
        self.arc_sword_index_list = []

        gap_x = 50 
        start_x = self.player.rect.centerx - (gap_x * 2)  
        y = self.player.rect.top - 80

        for i in range(5):
            pos = (start_x + i * gap_x, y)
            sword = ArcSwordFollow(self.player, pos, [self.knive_group])
            self.arc_swords.append(sword)
        self.arc_sword_index_list = list(range(len(self.arc_swords)))
        random.shuffle(self.arc_sword_index_list)

    def update_arc_swords(self, dt):
        if not self.arc_swords:
            return
        for sword in self.arc_swords:
            if sword.follow_player:
                sword.update_follow()
        self.arc_shoot_timer += dt
        if self.arc_shoot_timer >= self.arc_shoot_delay and self.arc_sword_index_list:
            self.arc_shoot_timer = 0
            idx = self.arc_sword_index_list.pop()
            sword = self.arc_swords[idx]
            sword.shoot_towards_player()
        if not self.arc_sword_index_list and all(not sword.follow_player for sword in self.arc_swords):
            self.arc_swords.clear()
            self.arc_cooldown_timer = 0  

    def ult(self):
        self.is_uliting = True
        self.ult_timer = 0
        self.play_animation('UltIn')
        map = load_pygame(join('data', 'maps', 'noliictu.tmx'))
        for marker in map.get_layer_by_name('entities'):
            if marker.name == 'Ult':
                teleport_pos = (marker.x, marker.y)
                self.rect.center = teleport_pos
                break
            
    def attack(self, dt):
        if not self.attacking:
            self.attacking = True
            self.knives_fired = 0
            self.knife_timer = 0
            self.play_animation('Attack')

        self.knife_timer += dt
        if self.knife_timer >= self.knife_interval and self.knives_fired < self.max_knives:
            self.knife_timer = 0
            self.knives_fired += 1

            offset = pygame.Vector2(70, 0) if self.player.rect.centerx > self.rect.centerx else pygame.Vector2(-70, 0)
            spawn_pos = pygame.Vector2(self.rect.center) - offset
            Knive(spawn_pos, self.player.player_hitbox.midbottom, [self.knive_group], self.player)

        if self.knives_fired >= self.max_knives:
            self.attacking = False
            self.attack_cooldown_timer = 0
            self.play_animation('Idle')

    def move():
        pass

    def update(self, dt):
        super().update(dt)
        self.detection_rect.center = self.rect.center
        num = random.randint(1, 9)

        if self.dying:
            frames = self.animations[self.status]
            if self.status == 'TeleportOut' and self.frame_index >= len(frames) - 1:
                self.kill()
            return

        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt

        self.arc_cooldown_timer += dt
        if self.arc_cooldown_timer >= self.arc_cooldown:
            if not self.arc_swords:
                self.spawn_arc_swords()

        self.update_arc_swords(dt)

        if self.hp <= 3000:
            self.ult_cooldown_timer += dt
            if self.hp<= 1500:
                if self.ult_cooldown_timer >= self.ult_cooldown and not self.is_uliting and not self.after_ult_teleport and not self.recovering_after_ult and not self.attacking:
                    self.ult()
                    self.ult_cooldown_timer = 0
                    return

        if self.can_ult and not self.is_uliting:
            self.ult()
            self.can_ult = False
            return

        if self.is_uliting:
            frames = self.animations[self.status]
            if self.status == 'UltIn':
                if self.frame_index >= len(frames) - 1:
                    self.play_animation('Ult')
            elif self.status == 'Ult':
                self.ult_timer += dt
                self.ult_spawn_timer += dt

                if self.ult_spawn_timer >= self.ult_spawn_interval:
                    self.ult_spawn_timer = 0
                    RainKnive([self.ult_knives_group], self.player)

                if self.ult_timer >= self.ult_duration:
                    self.is_uliting = False
                    self.after_ult_teleport = True
                    self.play_animation('TeleportOut')
            return

        if self.after_ult_teleport:
            frames = self.animations[self.status]
            if self.status == 'TeleportOut' and self.frame_index >= len(frames) - 1:
                map = load_pygame(join('data', 'maps', 'noliictu.tmx'))
                possible_markers = [marker for marker in map.get_layer_by_name('entities') if marker.name.isdigit()]
                if possible_markers:
                    teleport_marker = random.choice(possible_markers)
                    teleport_pos = (teleport_marker.x, teleport_marker.y)
                    self.rect.center = teleport_pos
                self.play_animation('TeleportIn')
            elif self.status == 'TeleportIn' and self.frame_index >= len(frames) - 1:
                self.after_ult_teleport = False
                self.recovering_after_ult = True
                self.attack_cooldown_timer = self.attack_cooldown  # supaya bisa langsung menyerang setelah recover
                self.attacking = False
                self.play_animation('Idle')
                self.attack(0)
            return

        if self.recovering_after_ult:
            self.attack_cooldown_timer += dt
            if self.attack_cooldown_timer >= self.attack_cooldown:
                self.recovering_after_ult = False
            return

        if self.teleporting:
            frames = self.animations[self.status]
            if self.status == 'TeleportOut' and self.frame_index >= len(frames) - 1:
                map = load_pygame(join('data', 'maps', 'noliictu.tmx'))
                for marker in map.get_layer_by_name('entities'):
                    if marker.name == f'{num}':
                        teleport_pos = (marker.x, marker.y)
                        self.rect.center = teleport_pos
                        break
                self.play_animation('TeleportIn')
            elif self.status == 'TeleportIn' and self.frame_index >= len(frames) - 1:
                self.teleporting = False
                self.teleport_cooldown = 8
                self.attack_cooldown_timer = self.attack_cooldown
                self.attacking = False
                self.play_animation('Idle')
                self.attack(0)
        else:
            if self.detection_rect.colliderect(self.player.rect):
                self.time_in_rect += dt
            else:
                self.time_in_rect = 0

            if self.time_in_rect >= 2.5 and self.teleport_cooldown <= 0 and not self.is_uliting and not self.after_ult_teleport and not self.recovering_after_ult:
                self.play_animation('TeleportOut')
                self.teleporting = True
                self.attacking = False
                self.time_in_rect = 0
            else:
                if self.attacking:
                    self.attack(dt)
                else:
                    self.attack_cooldown_timer += dt
                    if self.attack_cooldown_timer >= self.attack_cooldown:
                        self.attack(dt)
                    elif self.status != 'Idle':
                        self.play_animation('Idle')
            
        
        self.hitbox.center = self.rect.center

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0 and not self.dying:
            self.hp = 0
            self.dying = True
            self.play_animation('TeleportOut')

    def draw_detection_rect(self, surface):
        if self.detection_active:
            pygame.draw.rect(surface, (255, 0, 0), self.detection_rect, 2)