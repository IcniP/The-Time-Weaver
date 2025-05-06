import pygame
from settings import *
from entity import Player
from os import listdir
from os.path import join, dirname, abspath

class Cervus(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player):
        super().__init__(groups)
        self.animations = {'Idle': [], 'LeftHand': [], 'RightHand': []}
        self.import_assets()
        self.status = 'Idle'
        self.frame_index = 0
        self.animation_speed = 6

        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        
        self.left_hand = pygame.sprite.Sprite(groups)
        self.right_hand = pygame.sprite.Sprite(groups)
        self.left_hand.image = self.animations['LeftHand'][0]
        self.right_hand.image = self.animations['RightHand'][0]
        self.left_hand.rect = self.left_hand.image.get_rect()
        self.right_hand.rect = self.right_hand.image.get_rect()
        self.left_hand.rect.center = pos  
        self.right_hand.rect.center = pos  
        self.player = player
        self.hand_speed = 10

    def import_assets(self):
        """Load all assets for Cervus, including left and right hands."""
        base_path = join(dirname(abspath(__file__)), '..', 'Assets', 'Enemy', 'Final')
        self.animations['Idle'] = self.import_folder(join(base_path, 'enemy final 1st'))
        self.animations['LeftHand'] = self.import_folder(join(base_path, 'left', 'idle'))
        self.animations['RightHand'] = self.import_folder(join(base_path, 'right', 'idle'))

    def import_folder(self, path):
        """Load all images from a folder."""
        images = []
        for file_name in sorted(listdir(path), key=lambda x: int(x.split('.')[0])):
            full_path = join(path, file_name)
            image = pygame.image.load(full_path).convert_alpha()
            images.append(image)
        return images

    def animate(self, dt):
        """Handle animation updates."""
        frames = self.animations[self.status]
        self.frame_index += self.animation_speed * dt

        if self.frame_index >= len(frames):
            self.frame_index = 0

        self.image = frames[int(self.frame_index)]
    
    def update_hands(self):
       
        player_x, player_y = self.player.rect.center
        cervus_x, cervus_y = self.rect.center

        # --- LEFT HAND ---
        if player_x < cervus_x:
            target_left_x = player_x - 50
            target_left_y = player_y - 100

            self.left_hand.rect.x += (target_left_x - self.left_hand.rect.x) / (self.hand_speed * 1.5)
            self.left_hand.rect.y += (target_left_y - self.left_hand.rect.y) / (self.hand_speed * 1.5)

        # Kalau terlalu jauh dari Cervus (>400px), tarik balik
        distance_left = ((self.left_hand.rect.centerx - cervus_x) ** 2 + (self.left_hand.rect.centery - cervus_y) ** 2) ** 0.5
        if distance_left > 400:
            self.left_hand.rect.x += (cervus_x - self.left_hand.rect.centerx) / (self.hand_speed)
            self.left_hand.rect.y += (cervus_y - self.left_hand.rect.centery) / (self.hand_speed)

        # Update gambar
        self.left_hand.image = self.animations['LeftHand'][int(self.frame_index)]
        self.left_hand.rect.x = max(0, min(self.left_hand.rect.x, WINDOW_WIDTH - self.left_hand.rect.width))
        self.left_hand.rect.y = max(0, min(self.left_hand.rect.y, WINDOW_HEIGHT - self.left_hand.rect.height))

        # --- RIGHT HAND ---
        if player_x > cervus_x:
            target_right_x = player_x + 50
            target_right_y = player_y - 100

            self.right_hand.rect.x += (target_right_x - self.right_hand.rect.x) / (self.hand_speed * 1.5)
            self.right_hand.rect.y += (target_right_y - self.right_hand.rect.y) / (self.hand_speed * 1.5)

        # Kalau terlalu jauh dari Cervus (>400px), tarik balik
        distance_right = ((self.right_hand.rect.centerx - cervus_x) ** 2 + (self.right_hand.rect.centery - cervus_y) ** 2) ** 0.5
        if distance_right > 400:
            self.right_hand.rect.x += (cervus_x - self.right_hand.rect.centerx) / (self.hand_speed)
            self.right_hand.rect.y += (cervus_y - self.right_hand.rect.centery) / (self.hand_speed)

        # Update gambar
        self.right_hand.image = self.animations['RightHand'][int(self.frame_index)]
        self.right_hand.rect.x = max(0, min(self.right_hand.rect.x, WINDOW_WIDTH - self.right_hand.rect.width))
        self.right_hand.rect.y = max(0, min(self.right_hand.rect.y, WINDOW_HEIGHT - self.right_hand.rect.height))

    def update(self, dt):
        
        self.animate(dt)
        self.update_hands()