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
        self.ready_to_teleport = False  # Baru teleport kalau ini True

    def update(self, dt):
        super().update(dt)

        self.detection_rect.center = self.rect.center

        # Hitung cooldown teleport
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt

        if self.teleporting:
            frames = self.animations[self.status]

            # Selesai TeleportOut ➔ TeleportIn
            if self.status == 'TeleportOut' and self.frame_index >= len(frames) - 1:
                self.play_animation('TeleportIn')

            # Selesai TeleportIn ➔ Idle
            elif self.status == 'TeleportIn' and self.frame_index >= len(frames) - 1:
                self.play_animation('Idle')
                self.teleporting = False
                self.teleport_cooldown = 3  # cooldown 3 detik
                self.ready_to_teleport = False  # setelah teleport selesai, harus reset tunggu 5 detik lagi

        # Kalau tidak sedang teleport
        if not self.teleporting and self.teleport_cooldown <= 0:
            if self.detection_rect.colliderect(self.player.rect):
                self.time_in_rect += dt
            else:
                self.time_in_rect = 0

            # Kalau player stay 5 detik di area
            if self.time_in_rect >= 5:
                self.play_animation('TeleportOut')
                self.teleporting = True
                self.time_in_rect = 0  # Reset lagi waktu player stay
        else:
            # Kalau masih cooldown atau teleport, reset hitungannya
            self.time_in_rect = 0

    def draw_detection_rect(self, surface):
        if self.detection_active:
            pygame.draw.rect(surface, (255, 0, 0), self.detection_rect, 2)


