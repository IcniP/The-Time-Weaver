from settings import *


class allsprite(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.Screen = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self,target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH/ 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT/ 2)
        ground_sprite = [sprite for sprite in self if hasattr(sprite, 'ground')]
        object_sprite  = [sprite for sprite in self if not hasattr(sprite, 'ground')]
        
        for layer in [ground_sprite,object_sprite]:
            for sprite in sorted(layer,key =lambda sprite: sprite.rect.centery):
                self.Screen.blit(sprite.image,sprite.rect.topleft + self.offset)

class player(pygame.sprite.Sprite):
    def __init__(self,pos, groups , collision_sprite):
        super().__init__(groups)
 
        self.load_image()
        self.state, self.frame_index = 'down',0
        self.image = pygame.image.load(join('Assets','player','idle','1.png')).convert_alpha()
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-60,-90)
        self.speed = 500
        self.direction = pygame.Vector2(0,0)
        self.collision_sprite = collision_sprite         

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a]or keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_s]or keys[pygame.K_DOWN]) - int(keys[pygame.K_w]or keys[pygame.K_UP])
        if self.direction.length() > 0 :
            self.direction = self.direction.normalize()

    def move(self,dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprite:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0 : self.hitbox_rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0 : self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0 : self.hitbox_rect.top = sprite.rect.bottom

    def update(self,dt):
        self.input()
        self.move(dt)
        






