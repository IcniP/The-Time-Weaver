import pygame
from settings import *
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

        # Add shake
        game = pygame.display.get_wm_info().get('window')  # dirty hack to get Game reference
        if hasattr(game, 'shake_timer') and game.shake_timer > 0:
            shake_x = random.randint(-game.shake_intensity, game.shake_intensity)
            shake_y = random.randint(-game.shake_intensity, game.shake_intensity)
            self.offset += pygame.Vector2(shake_x, shake_y)

        for sprite in self:
            if sprite.image and sprite.rect:
                self.display_surface.blit(sprite.image, pygame.Vector2(sprite.rect.topleft) + self.offset)
            if hasattr(sprite, 'draw'):
                sprite.draw(self.display_surface, self.offset)
            if hasattr(sprite, 'hand_image') and sprite.hand_image is not None:
                self.display_surface.blit(sprite.hand_image, sprite.rect.topleft + pygame.Vector2(0, -5) + self.offset)

class Sprite(pygame.sprite.Sprite):
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


class KnifeDrop(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player):
        super().__init__(groups)
        self.player = player

        base_path = join('Assets', 'ui', 'knife_in_world')
        self.frames = [pygame.image.load(join(base_path, f'{i}.png')).convert_alpha() for i in range(4)]  # adjust count
        self.frame_index = 0
        self.animation_speed = 6
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0

    def update(self, dt):
        # Hover effect
        self.timer += self.animation_speed * dt
        if self.timer >= 1:
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

        if self.rect.colliderect(self.player.player_hitbox):
            self.player.knives += 1
            self.kill()