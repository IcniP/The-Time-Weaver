import pygame
from settings import *
from os import listdir
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.animations = {'Idle': [], 'Move': [], 'Attack': [], 'Jump': []}
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

        # attack
        self.attacking = False

    def import_assets(self):
        base_path = r'E:\Coding\python\The Time Weaver\Assets\Player'
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

    def input(self):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        # Reset horizontal direction
        self.direction.x = 0

        if mouse_pressed[0]:  # Left mouse button
            self.attacking = True
        elif keys[pygame.K_SPACE]:
            if self.on_ground():
                self.direction.y = self.jump_speed
        else:
            self.attacking = False
            if keys[pygame.K_a]:
                self.direction.x = -1
            if keys[pygame.K_d]:
                self.direction.x = 1

    def on_ground(self):
        return self.rect.bottom >= WINDOW_HEIGHT  # Assume ground is bottom of screen

    def move(self, dt):
        self.direction.y += self.gravity * dt  # Apply gravity
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * dt

        # Floor collision
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.direction.y = 0

    def animate(self, dt):
        if self.attacking:
            self.status = 'Attack'
        elif self.direction.y < 0:
            self.status = 'Jump'
        elif self.direction.x != 0:
            self.status = 'Move'
        else:
            self.status = 'Idle'

        frames = self.animations[self.status]
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
