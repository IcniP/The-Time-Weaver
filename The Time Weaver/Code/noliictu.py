import pygame
from settings import *
from bossbase import BossBase
from os.path import join

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

        self.hp = 300

        self.detection_rect = pygame.Rect(self.rect.centerx - 200, self.rect.centery - 200, 400, 400)
        self.detection_active = False
        self.time_in_rect = 0
        self.teleporting = False
        self.teleport_cooldown = 0
        self.ready_to_teleport = False  

    def update(self, dt):
        super().update(dt)

        self.detection_rect.center = self.rect.center

        #cooldown teleport
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt

        if self.teleporting:
            frames = self.animations[self.status]

            if self.status == 'TeleportOut' and self.frame_index >= len(frames) - 1:
                self.play_animation('TeleportIn')

            elif self.status == 'TeleportIn' and self.frame_index >= len(frames) - 1:
                self.play_animation('Idle')
                self.teleporting = False
                self.teleport_cooldown = 5  
                self.ready_to_teleport = False  

        
        if not self.teleporting and self.teleport_cooldown <= 0:
            if self.detection_rect.colliderect(self.player.rect):
                self.time_in_rect += dt
            else:
                self.time_in_rect = 0

            # player detect
            if self.time_in_rect >= 5:
                self.play_animation('TeleportOut')
                self.teleporting = True
                self.time_in_rect = 0  
        else:
            self.time_in_rect = 0

    def draw_detection_rect(self, surface):
        if self.detection_active:
            pygame.draw.rect(surface, (255, 0, 0), self.detection_rect, 2)


