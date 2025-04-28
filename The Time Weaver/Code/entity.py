import pygame
from settings import *
from os import listdir
from os.path import join, dirname, abspath

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.animations = {'Idle': [], 'Move': [], 'Attack': [], 'Jump': [], 'Fall': []}
        self.import_assets()
        self.status = 'Idle'
        self.frame_index = 0
        self.animation_speed = 6

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        # movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 200  # pixels per second
        self.gravity = 500
        self.jump_speed = -300
        self.jumping = False
        self.facing_right = True # Facing right

        # attack
        self.attacking = False

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


#-----------------------------movement, animation, and all dat------------------------------------------

    #method attack
    def attack(self, button):
        if button[0]:
            self.attacking = True

    #method jump
    def jump(self, keys):
        if keys[pygame.K_SPACE] and self.on_ground() and not self.jumping:
            self.direction.y = self.jump_speed
            self.jumping = True
            
    def input(self):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        # Reset horizontal direction
        self.direction.x = 0
        
        #call attack method
        self.attack(mouse_pressed)
        #call jump method
        self.jump(keys)
        
        #walk
        if keys[pygame.K_a]:
            self.direction.x = -1
        if keys[pygame.K_d]:
            self.direction.x = 1

    def move(self, dt):
        self.direction.y += self.gravity * dt  # Apply gravity
        self.rect.x += self.direction.x * self.speed * dt #Apply consistent speed
        self.rect.y += self.direction.y * dt

        # Floor collision
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.direction.y = 0
            self.jumping = False

        #direction move
        if self.direction.x > 0:
            self.facing_right = True
        elif self.direction.x < 0:
            self.facing_right = False

    #method for on ground check
    def on_ground(self):
        return self.rect.bottom >= WINDOW_HEIGHT  # Assume ground is bottom of screen
    
    def animate(self, dt):
        #animation conditions
        if self.attacking:
            self.status = 'Attack'
        elif self.direction.y < 0:
            self.status = 'Jump'
        elif self.direction.y > 0 and not self.on_ground():
            self.status = 'Fall'
        elif self.direction.x != 0:
            self.status = 'Move'
        elif self.direction.x == 0:
            self.status = 'Idle'

        #custom animation speed for attack
        frames = self.animations[self.status]
        if self.status == 'Attack':
            self.frame_index += 10 * dt
        #animation speed for all
        else:
            self.frame_index += self.animation_speed * dt

        #reset animation attack only after finished
        if self.status == 'Attack' and self.frame_index >= len(frames):
            self.frame_index = 0
            self.attacking = False
        elif self.frame_index >= len(frames):
            self.frame_index = 0

        self.image = frames[int(self.frame_index)]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)

        #direction move
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)