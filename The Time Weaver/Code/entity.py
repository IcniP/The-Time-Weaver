import pygame
from settings import *
from os import listdir
from os.path import join, dirname, abspath

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.animations = {'Idle': [], 'Move': [], 'Attack': [], 'Attack2': [], 'Jump': [], 'Fall': []}
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 6
        self.state = 'idle'
        self.image = self.animations[self.get_animation_key()][self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        # movement n jump
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 200  # pixels per second
        self.gravity = 500
        self.jump_speed = -300
        self.jumping = False
        self.facing_right = True

        # attack
        self.attacking = False
        self.attacking_two = False
        self.attack_locked = False
        self.attack_button_pressed = False
        self.max_combo = 2
        self.current_combo = 1
        self.combo_reset_time = 5000  # miliseconds before combo reset
        self.last_attack_time = 0  # for combo timing

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
            elif self.current_combo == 2 and not self.attacking_two:
                self.attacking_two = True
                self.attack_locked = True
                self.frame_index = 0
                self.state = 'attack2'
        elif not mouse_pressed[0]:
            self.attack_button_pressed = False

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
    
#-----------------------------gravity stuff------------------------------------------
    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt  # Apply gravity
        self.rect.x += self.direction.x * self.speed * dt #Apply consistent speed
        self.rect.y += self.direction.y * dt

        # Floor collision
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.direction.y = 0
            self.jumping = False

    #method for on ground check
    def on_ground(self):
        return self.rect.bottom >= WINDOW_HEIGHT  # Assume ground is bottom of screen

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
        elif self.direction.y > 1 and not self.on_ground():
            self.state = 'fall'
        elif self.direction.x != 0:
            self.state = 'move'
        else:
            self.state = 'idle'

    def update_animation(self, dt):
        frames = self.animations[self.get_animation_key()]
        self.frame_index += 6 * dt if 'attack' not in self.state else 5 * dt

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
        self.move()
        self.add_gravity(dt)
        self.update_state()
        self.update_animation(dt)

        # Reset combo if too much time passed
        if pygame.time.get_ticks() - self.last_attack_time > self.combo_reset_time:
            self.current_combo = 1