from settings import *

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