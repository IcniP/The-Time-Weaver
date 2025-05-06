import pygame
from settings import *
from os import listdir
from os.path import join, dirname, abspath
from abc import ABC, abstractmethod

#-----------------------------Sprite thingy------------------------------------------
class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2(0, 0)

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        for sprite in self:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

#-----------------------------Entity->Player n Enemies------------------------------------------
class Entity(pygame.sprite.Sprite, ABC):
    def __init__(self, groups):
        super().__init__(groups)
    @abstractmethod
    def import_assets(self):
        pass

    @abstractmethod
    def import_folder(self, path):
        pass

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def update(self, dt):
        pass

class Player(Entity):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.animations = {'Idle': [], 'Move': [], 'Attack': [], 'Attack2': [], 'Jump': [], 'Fall': []}
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 6
        self.state = 'idle'
        self.image = self.animations[self.get_animation_key()][self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)
        self.collision_sprites = collision_sprites
        self.groupss = groups #all_sprites

        # movement n jump
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 200  # pixels per second
        self.gravity = 50
        self.jump_speed = -15
        self.jumping = False
        self.facing_right = True

        # attack
        self.attacking = False
        self.attacking_two = False
        self.attack_locked = False
        self.attack_button_pressed = False
        self.max_combo = 2
        self.current_combo = 1
        self.combo_reset_time = 1000  # miliseconds before combo reset
        self.last_attack_time = 0  # for combo timing

        self.player_hitwidth = 16
        self.player_hitheight = 32
        self.player_hitbox = pygame.Rect(0, 0, self.player_hitwidth, self.player_hitheight)

#-----------------------------Import------------------------------------------
    def import_assets(self):
        base_path = join(dirname(abspath(__file__)), '..', 'Assets', 'Player')
        for action in self.animations.keys():
            full_path = join(base_path, action)
            self.animations[action] = self.import_folder(full_path)

    def import_folder(self, path):
        images = []
        for file_name in sorted(listdir(path), key=lambda x: int(x.split('.')[0])):
            full_path = join(path, file_name)
            image = pygame.image.load(full_path).convert_alpha()
            images.append(image)
        return images


#-----------------------------movements and all dat------------------------------------------
    #method jump
    def jump(self, keys):
        if keys[pygame.K_SPACE] and self.on_ground() and not self.jumping:
            self.direction.y = self.jump_speed
            self.jumping = True
            
    #method move / for input etc
    def move(self):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        # Horizontal movement
        self.direction.x = 0
        if keys[pygame.K_a]:
            self.direction.x = -1
        if keys[pygame.K_d]:
            self.direction.x = 1

        #direction move
        if self.direction.x > 0:
            self.facing_right = True
        elif self.direction.x < 0:
            self.facing_right = False

        # Jump
        self.jump(keys)

        # Attack input (mouse click)
        self.attack(mouse_pressed)
    
    #method attack
    def attack(self, mouse_pressed):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.combo_reset_time:
            self.current_combo = 1

        if mouse_pressed[0] and not self.attack_button_pressed:
            self.attack_button_pressed = True
            self.last_attack_time = current_time
            if self.current_combo == 1 and not self.attacking:
                self.attacking = True
                self.attack_locked = True
                self.frame_index = 0
                self.state = 'attack1'

                hitbox = self.attack_hitbox()
                for enemy in self.groupss:
                    if isinstance(enemy, Humanoid) and hitbox.colliderect(enemy.entity_hitbox):
                        enemy.take_damage(1)
            elif self.current_combo == 2 and not self.attacking_two:
                self.attacking_two = True
                self.attack_locked = True
                self.frame_index = 0
                self.state = 'attack2'

                hitbox = self.attack_hitbox()
                for enemy in self.groupss:
                    if isinstance(enemy, Humanoid) and hitbox.colliderect(enemy.entity_hitbox):
                        enemy.take_damage(1)
                        
        elif not mouse_pressed[0]:
            self.attack_button_pressed = False
    
    def attack_hitbox(self):
        hitbox = self.player_hitbox.copy()
        hitbox.height = 32  # Set the height of the attack hitbox to match the player's height
        if self.facing_right:
            hitbox.width += 25
        else:
            hitbox.width -= 40
        return hitbox
    
#-----------------------------gravity stuff------------------------------------------
    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt  # Apply gravity
        self.player_hitbox.y += self.direction.y
        self.collision('vertical')

        self.player_hitbox.x += self.direction.x * self.speed * dt #Apply consistent speed
        self.collision('horizontal')

        self.rect.center = self.player_hitbox.center  # Update the rect position
    
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.player_hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.player_hitbox.right = sprite.rect.left
                    if self.direction.x < 0: self.player_hitbox.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0: 
                        self.player_hitbox.bottom = sprite.rect.top
                        self.direction.y = 0
                        self.jumping = False
                    if self.direction.y < 0: 
                        self.player_hitbox.top = sprite.rect.bottom
                        self.direction.y = 0
        self.rect.center = self.player_hitbox.center  # Update the rect position

    #method for on ground check
    def on_ground(self):
        self.player_hitbox.y += 1  # Temporarily move the player down by 1 pixel
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.player_hitbox):
                self.player_hitbox.y -= 1  # Reset the player's position
                return True
        self.player_hitbox.y -= 1  # Reset the player's position
        return False

#-----------------------------animation matter------------------------------------------
    def get_animation_key(self):
        mapping = {
            'idle': 'Idle',
            'move': 'Move',
            'jump': 'Jump',
            'fall': 'Fall',
            'attack1': 'Attack',
            'attack2': 'Attack2'
        }
        return mapping[self.state]

    def update_state(self):
        if self.attacking or self.attacking_two:
            return  # Don't change state mid-attack

        if self.direction.y < 0:
            self.state = 'jump'
            self.collision('vertical')
        elif self.direction.y > 1 and not self.on_ground():
            self.state = 'fall'
            self.collision('vertical')
        elif self.direction.x != 0:
            self.state = 'move'
            self.collision('horizontal')
        else:
            self.state = 'idle'

    def update_animation(self, dt):
        frames = self.animations[self.get_animation_key()]
        self.frame_index += 6 * dt if 'attack' not in self.state else 8 * dt

        if self.frame_index >= len(frames):
            self.frame_index = 0

            # Finish attack
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
        
    def update(self, dt):
        self.player_hitbox.center = self.rect.center
        self.move()
        self.add_gravity(dt)
        self.update_state()
        self.update_animation(dt)

        # Reset combo if too much time passed
        if pygame.time.get_ticks() - self.last_attack_time > self.combo_reset_time:
            self.current_combo = 1

class Humanoid(Entity):
    def __init__(self, type, pos, groups, collision_sprites):
        super().__init__(groups)
        self.type = type
        self.animations = {'Idle': [], 'Move': [], 'Attack': []}
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 6
        self.state = 'idle'
        self.image = self.animations[self.get_animation_key()][self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)
        self.collision_sprites = collision_sprites
        
        # movement n jump
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 100  # pixels per second
        self.gravity = 50
        self.facing_right = True

        # attack
        self.attacking = False

        self.entity_hitwidth = 16
        self.entity_hitheight = 32
        self.entity_hitbox = pygame.Rect(0, 0, self.entity_hitwidth, self.entity_hitheight)

        #hp
        if self.type == 'Sword':
            self.hp = 2
        elif self.type == 'Spear':
            self.hp = 3
        elif self.type == 'Axe':
            self.hp = 4
        
        self.death_time = 0
        self.death_duration = 400

#-----------------------------Import------------------------------------------
    def import_assets(self):
        base_path = join(dirname(abspath(__file__)), '..', 'Assets', 'Enemy', 'Skelly', self.type)
        for action in self.animations.keys():
            full_path = join(base_path, action)
            self.animations[action] = self.import_folder(full_path)

    def import_folder(self, path):
        images = []
        for file_name in sorted(listdir(path), key=lambda x: int(x.split('.')[0])):
            full_path = join(path, file_name)
            image = pygame.image.load(full_path).convert_alpha()
            images.append(image)
        return images


    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.die()
    
    def die(self):
        self.death_time = pygame.time.get_ticks()
        
        mask = pygame.mask.from_surface(self.image)
        white_surf = mask.to_surface(setcolor=(255, 100, 0), unsetcolor=(0, 0, 0, 0))
        white_surf.set_colorkey((0, 0, 0))
        self.image = white_surf

        # Stop all movement and actions
        self.direction = pygame.math.Vector2(0, 0)
        self.attacking = False


#-----------------------------movements and all dat------------------------------------------
    def move(self, dt):
        pass

#-----------------------------gravity stuff------------------------------------------
    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt  # Apply gravity
        self.entity_hitbox.y += self.direction.y * dt  # Apply gravity to the rect
        self.collision('vertical')

        self.entity_hitbox.x += self.direction.x * self.speed * dt  # Apply consistent speed
        self.collision('horizontal')

        self.rect.center = self.entity_hitbox.center  # Update the rect position

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.entity_hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.entity_hitbox.right = sprite.rect.left
                    if self.direction.x < 0: self.entity_hitbox.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0: 
                        self.entity_hitbox.bottom = sprite.rect.top
                        self.direction.y = 0
                    if self.direction.y < 0: 
                        self.entity_hitbox.top = sprite.rect.bottom
                        self.direction.y = 0
        self.rect.center = self.entity_hitbox.center  # Update the rect position
    
    # def on_ground(self):
    #     self.entity_hitbox.y += 1
    #     for sprite in self.collision_sprites:
    #         if sprite.rect.colliderect(self.entity_hitbox):
    #             self.entity_hitbox.y -= 1
    #             return True
    #     self.entity_hitbox.y -= 1
    #     return False

#-----------------------------animation matter------------------------------------------
    def get_animation_key(self):
        mapping = {
            'idle': 'Idle',
            'move': 'Move',
            'attack': 'Attack'
        }
        return mapping[self.state]
        
    def update_state(self):
        if self.attacking:
            return
        
        if self.direction.x != 0:
            self.state = 'move'
            self.collision('horizontal')
        else:
            self.state = 'idle'
    
    def update_animation(self, dt):
        frames = self.animations[self.get_animation_key()]
        self.frame_index += 6 * dt if 'attack' not in self.state else 8 * dt

        if self.frame_index >= len(frames):
            self.frame_index = 0

            # Finish attack
            if self.state == 'attack':
                self.attacking = False
                self.state = 'idle'

        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if self.death_time == 0:
            self.entity_hitbox.center = self.rect.center
            self.move(dt)
            self.add_gravity(dt)
            self.update_state()
            self.update_animation(dt)
        else:
            if current_time - self.death_time >= self.death_duration:
                self.kill()
        