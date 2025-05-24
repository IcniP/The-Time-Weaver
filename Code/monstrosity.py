from settings import *
from entity import *
from effects import *

class Monstrosity(Entity):
    def __init__(self, pos, groups, collision_sprites, player):
        super().__init__(groups)
        self.player_ref = player
        self.groupss = groups
        self.animations = {}
        self.state = 'idle'
        self.frame_index = 0
        self.animation_speed = 6

        self.collision_sprites = collision_sprites
        self.direction = pygame.math.Vector2(0, 0)
        self.gravity = 30
        self.speed = 100
        self.facing_right = True

        self.import_assets()
        self.image = self.animations[self.get_animation_key()]
        self.rect = self.image.get_rect(midbottom=pos)

        # Central 48x48 hitbox
        self.entity_hitbox = pygame.Rect(0, 0, 48, 48)
        self.entity_hitbox.center = self.rect.center

        #jump
        self.jump_cd = 2000
        self.last_jump_time = 0
        self.jump_speed = -11.5
        self.jump_distance = TILE_SIZE * 5
        self.impact_radius = TILE_SIZE * 2
        self.has_impacted = False

        #hp
        self.__hp = 5
        self.death_time = 0
        self.death_duration = 400
        

#-----------------------------------------------Importing thingy-----------------------------------------------
    def import_assets(self):
        base_path = join(dirname(abspath(__file__)), '..', 'Assets', 'Enemy', 'Bookie')
        self.animations['Idle'] = pygame.image.load(join(base_path, 'idle.png')).convert_alpha()
        self.animations['Jump'] = pygame.image.load(join(base_path, 'jump.png')).convert_alpha()
        self.animations['Fall'] = pygame.image.load(join(base_path, 'fall.png')).convert_alpha()
        
#-----------------------------------------------World interaction thingy-----------------------------------------------
    def add_gravity(self, dt):
        self.direction.y += self.gravity * dt
        self.entity_hitbox.y += self.direction.y
        self.collision('vertical')

        self.entity_hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        self.rect.center = self.entity_hitbox.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.entity_hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.entity_hitbox.right = sprite.rect.left
                    elif self.direction.x < 0: self.entity_hitbox.left = sprite.rect.right
                elif direction == 'vertical':
                    if self.direction.y > 0:
                        self.entity_hitbox.bottom = sprite.rect.top
                        self.direction.y = 0
                        self.direction.x = 0 #make bookie stay after fall n not sliding
                        self.handle_impact()
                    elif self.direction.y < 0:
                        self.entity_hitbox.top = sprite.rect.bottom
                        self.direction.y = 0
        self.rect.center = self.entity_hitbox.center

    def move(self, dt):
        now = pygame.time.get_ticks()
        px, py = self.player_ref.player_hitbox.center
        ex, ey = self.entity_hitbox.center

        distance_x = abs(px - ex)
        same_height = abs(py - ey) < TILE_SIZE

        if distance_x <= TILE_SIZE * 5 and same_height and self.direction.y == 0:
            if now - self.last_jump_time >= self.jump_cd:
                self.last_jump_time = now
                self.direction.y = self.jump_speed
                self.direction.x = 1 if px > ex else -1
                self.facing_right = self.direction.x < 0
                self.has_impacted = False
    
    def handle_impact(self):
        if self.has_impacted:
            return
        
        self.has_impacted = True
        self.state = 'idle'
        dust_pos = self.entity_hitbox.midbottom
        StompDust(dust_pos, self.groups())
        bookie_stomp.play()

        # Left stomp area
        left_hitbox = pygame.Rect(0, 0, TILE_SIZE * 2, TILE_SIZE)
        left_hitbox.bottomright = self.entity_hitbox.bottomleft

        # Right stomp area
        right_hitbox = pygame.Rect(0, 0, TILE_SIZE * 2, TILE_SIZE)
        right_hitbox.bottomleft = self.entity_hitbox.bottomright

        player_hitbox = self.player_ref.player_hitbox

        if (left_hitbox.colliderect(player_hitbox) or right_hitbox.colliderect(player_hitbox)) and not self.player_ref.invincible:
            self.player_ref.take_damage(1)
        
        if hasattr(self.player_ref, 'game'):
            self.player_ref.game.shake_timer = 0.2
            self.player_ref.game.shake_duration = 0.2
    
    def take_damage(self, damage):
        self.__hp -= damage
        bookie_hit.play()

        if hasattr(self, 'player_ref'):
            dx = self.entity_hitbox.centerx - self.player_ref.player_hitbox.centerx
            self.direction.x = 1 if dx > 0 else -1

            knockback_speed = 100
            knockback_upward = -300
            self.direction.x *= knockback_speed / self.speed
            self.direction.y = knockback_upward / self.gravity

        if self.__hp <= 0:
            bookie_die.play()
            self.die()
    
    def die(self, instant = False):
        if instant:
            self.kill()
            return

        self.death_time = pygame.time.get_ticks()
        mask = pygame.mask.from_surface(self.image)
        surf = mask.to_surface(setcolor=(255, 100, 0), unsetcolor=(0, 0, 0, 0))
        surf.set_colorkey((0, 0, 0))
        self.image = surf
        self.direction = pygame.math.Vector2(0, 0)
        self.attacking = False

        if random.randint(1, 100) <= 40:
            KnifeDrop(self.rect.center, self.groupss, self.player_ref)

#-----------------------------------------------Animation thingy-----------------------------------------------
    def get_animation_key(self):
        if self.direction.y < 0:
            return 'Jump'
        elif self.direction.y > 1:
            return 'Fall'
        return 'Idle'

    def update_state(self):
        if self.direction.y < 0:
            self.state = 'jump'
        elif self.direction.y > 1:
            self.state = 'fall'
        else:
            self.state = 'idle'

    def update_animation(self):
        self.image = self.animations[self.get_animation_key()]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, dt):
        now = pygame.time.get_ticks()

        if self.death_time == 0:
            self.entity_hitbox.center = self.rect.center
            self.move(dt)
            self.add_gravity(dt)
            self.update_state()
            self.update_animation()
        elif now - self.death_time >= self.death_duration:
            self.kill()