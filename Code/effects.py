from settings import *

#sounds
pygame.mixer.init()

heal = pygame.mixer.Sound(join('Assets', 'Sounds', 'heal.mp3'))
hurt = pygame.mixer.Sound(join('Assets', 'Sounds', 'hurt.mp3'))
swing = pygame.mixer.Sound(join('Assets', 'Sounds', 'swing.mp3'))
throw = pygame.mixer.Sound(join('Assets', 'Sounds', 'throw.mp3'))
throw.set_volume(0.2)

skelly_hit = pygame.mixer.Sound(join('Assets', 'Sounds', 'skelly-hit.mp3'))
skelly_hit.set_volume(0.4)
skelly_die = pygame.mixer.Sound(join('Assets', 'Sounds', 'skelly-die.mp3'))

bookie_hit = pygame.mixer.Sound(join('Assets', 'Sounds', 'bookie-hit.mp3'))
bookie_hit.set_volume(0.4)
bookie_die = pygame.mixer.Sound(join('Assets', 'Sounds', 'bookie-die.mp3'))
bookie_idle = pygame.mixer.Sound(join('Assets', 'Sounds', 'bookie-idle.mp3'))
bookie_stomp = pygame.mixer.Sound(join('Assets', 'Sounds', 'bookie-stomp.mp3'))
bookie_stomp.set_volume(0.8)

wraith_hit = pygame.mixer.Sound(join('Assets', 'Sounds', 'wraith-hit.mp3'))
wraith_hit.set_volume(0.4)
wraith_attack = pygame.mixer.Sound(join('Assets', 'Sounds', 'wraith-attack.mp3'))
wraith_attack.set_volume(0.4)

teleport = pygame.mixer.Sound(join('Assets', 'Sounds', 'teleport.mp3'))
sword_rain = pygame.mixer.Sound(join('Assets', 'Sounds', 'swordrain.mp3'))




class SlashEffect(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.frames = self.import_frames()
        self.frame_index = 0
        self.animation_speed = 10  # adjust as needed
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0

    def import_frames(self):
        path = join('Assets', 'Player', 'slasheffect')
        return [pygame.image.load(join(path, f)).convert_alpha()
                for f in sorted(listdir(path), key=lambda x: int(x.split('.')[0]))]

    def update(self, dt):
        self.timer += self.animation_speed * dt
        if self.timer >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.timer)]

#Impact Blastny si Wraith
class FireBlast(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.frames = self.import_frames()
        self.frame_index = 0
        self.animation_speed = 10  # adjust as needed
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0

    def import_frames(self):
        path = join('Assets', 'Enemy', 'Wraith', 'projectile', 'impact')
        return [pygame.image.load(join(path, f)).convert_alpha()
                for f in sorted(listdir(path), key=lambda x: int(x.split('.')[0]))]

    def update(self, dt):
        self.timer += self.animation_speed * dt
        if self.timer >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.timer)]

#stomp dustnya si Bookie
class StompDust(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.frames = self.import_frames()
        self.frame_index = 0
        self.frame_duration = 100  # ms per frame
        self.last_update_time = pygame.time.get_ticks()

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)

    def import_frames(self):
        path = join('Assets', 'Enemy', 'Bookie', 'dust')
        return [pygame.image.load(join(path, f'{i}.png')).convert_alpha() for i in range(3)]

    def update(self, dt):
        now = pygame.time.get_ticks()
        if now - self.last_update_time >= self.frame_duration:
            self.frame_index += 1
            self.last_update_time = now
            if self.frame_index >= len(self.frames):
                self.kill()
                return
            self.image = self.frames[self.frame_index]