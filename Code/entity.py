import pygame
from settings import *
from os import listdir
from os.path import join, dirname, abspath
from abc import ABC, abstractmethod

# ========================= Sprite Groups =========================
class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2(0, 0)

    #for camera
    def draw(self, target_pos, map_w, map_h):
        self.offset.x = max(min(-(target_pos[0] - WINDOW_WIDTH / 2), 0), WINDOW_WIDTH - map_w)
        self.offset.y = max(min(-(target_pos[1] - WINDOW_HEIGHT / 2), 0), WINDOW_HEIGHT - map_h)

        for sprite in self:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

            if hasattr(sprite, 'draw'):
                sprite.draw(self.display_surface, self.offset)
                
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


# ========================= Abstract Entity Class =========================
class Entity(pygame.sprite.Sprite, ABC):
    def __init__(self, groups):
        super().__init__(groups)

    @abstractmethod
    def import_assets(self): pass

    @abstractmethod
    def move(self): pass

    @abstractmethod
    def update(self, dt): pass 