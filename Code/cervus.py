from settings import *
from entity import Player
from bossbase import BossBase

class Cervus(BossBase):
    def __init__(self, pos, groups, player):
        animation_paths = {
            'Idle': ['cervus', '1st'],
            'LeftHand': ['cervus', 'left', 'idle'],
            'RightHand': ['cervus', 'right', 'idle']
        }
        super().__init__(pos, groups, player, boss_name='Cervus', animation_paths=animation_paths)

        self.hp = 1000  

        # Hands
        self.left_hand = pygame.sprite.Sprite(groups)
        self.right_hand = pygame.sprite.Sprite(groups)
        self.left_hand.image = self.animations['LeftHand'][0]
        self.right_hand.image = self.animations['RightHand'][0]
        self.left_hand.rect = self.left_hand.image.get_rect(center=pos)
        self.right_hand.rect = self.right_hand.image.get_rect(center=pos)

        self.hand_speed = 10

    def update_hands(self):
        player_x, player_y = self.player.rect.center
        cervus_x, cervus_y = self.rect.center

        if player_x < cervus_x:
            target_left_x = player_x - 50
            target_left_y = player_y - 100
            self.left_hand.rect.x += (target_left_x - self.left_hand.rect.x) / (self.hand_speed * 1.5)
            self.left_hand.rect.y += (target_left_y - self.left_hand.rect.y) / (self.hand_speed * 1.5)

        distance_left = ((self.left_hand.rect.centerx - cervus_x) ** 2 + (self.left_hand.rect.centery - cervus_y) ** 2) ** 0.5
        if distance_left > 400:
            self.left_hand.rect.x += (cervus_x - self.left_hand.rect.centerx) / self.hand_speed
            self.left_hand.rect.y += (cervus_y - self.left_hand.rect.centery) / self.hand_speed

        self.left_hand.image = self.animations['LeftHand'][int(self.frame_index)]
        self.left_hand.rect.x = max(0, min(self.left_hand.rect.x, WINDOW_WIDTH - self.left_hand.rect.width))
        self.left_hand.rect.y = max(0, min(self.left_hand.rect.y, WINDOW_HEIGHT - self.left_hand.rect.height))

        if player_x > cervus_x:
            target_right_x = player_x + 50
            target_right_y = player_y - 100
            self.right_hand.rect.x += (target_right_x - self.right_hand.rect.x) / (self.hand_speed * 1.5)
            self.right_hand.rect.y += (target_right_y - self.right_hand.rect.y) / (self.hand_speed * 1.5)

        distance_right = ((self.right_hand.rect.centerx - cervus_x) ** 2 + (self.right_hand.rect.centery - cervus_y) ** 2) ** 0.5
        if distance_right > 400:
            self.right_hand.rect.x += (cervus_x - self.right_hand.rect.centerx) / self.hand_speed
            self.right_hand.rect.y += (cervus_y - self.right_hand.rect.centery) / self.hand_speed

        self.right_hand.image = self.animations['RightHand'][int(self.frame_index)]
        self.right_hand.rect.x = max(0, min(self.right_hand.rect.x, WINDOW_WIDTH - self.right_hand.rect.width))
        self.right_hand.rect.y = max(0, min(self.right_hand.rect.y, WINDOW_HEIGHT - self.right_hand.rect.height))

    def update(self, dt):
        super().update(dt)  
        self.update_hands() 