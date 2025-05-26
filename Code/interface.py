from settings import *

class UserInterface:
    def __init__(self, surface):
        self.display = surface
        
        self.health_bars = self.load_frames('Assets/ui/hp_bar')
        self.stamina_bars = self.load_frames('Assets/ui/stamina_bar')
        self.knives = self.load_frames('Assets/ui/knives')
        self.potions = self.load_frames_potion('Assets/ui/potions')
    
    def load_frames(self, folder_path):
        frames = []
        for i in range(5):
            path = join(folder_path, f'{i}.png')
            image = pygame.transform.scale2x(pygame.image.load(path).convert_alpha()) #uiny di 2x
            frames.append(image)
        return frames
    
    def load_frames_potion(self, folder_path):
        frames = []
        for i in range(3):
            path = join(folder_path, f'{i}.png')
            image = pygame.transform.scale2x(pygame.image.load(path).convert_alpha())
            frames.append(image)
        return frames

    #nampilin hp bar
    def draw_bar(self, frames, current, max_value, position, bg = None):
        ratio = max(0, min(current/max_value, 1))
        index = int(ratio * (len(frames)-1))
        frame = frames[index]

        if bg:
            self.display.blit(bg, position)
        self.display.blit(frame, position)

    #nampilin stamina bar
    def draw(self, player):
        self.draw_bar(
            frames = self.health_bars,
            current = player.get_hp(),
            max_value = player.max_hp,
            position = (10, 10),
        )
        self.draw_bar(
            frames = self.stamina_bars,
            current = player.get_stamina(),
            max_value = player.max_stamina,
            position = (10, 10),
        )
        self.draw_bar(
            frames = self.knives,
            current = player.knives,
            max_value = player.max_knives,
            position = (10, 68)
        )
        self.draw_bar(
            frames = self.potions,
            current = player.potions,
            max_value = player.max_potions,
            position = (64, 20)
        )
 #mista Jesta
class BossHealthBar:
    def __init__(self, max_health, length, pos, name='Boss'):
        self.max_health = max_health
        self.current_health = max_health
        self.target_health = max_health
        self.health_bar_length = length
        self.health_ratio = self.max_health / self.health_bar_length
        self.health_change_speed = 5
        self.pos = pos  # (x, y)
        self.name = name

    def update(self, current_hp):
        self.target_health = max(0, min(current_hp, self.max_health))

    def draw(self, surface):
        transition_width = 0
        transition_color = (255, 0, 0)

        if self.current_health < self.target_health:
            self.current_health += self.health_change_speed
            transition_width = int((self.target_health - self.current_health) / self.health_ratio)
            transition_color = (0, 255, 0)
        elif self.current_health > self.target_health:
            self.current_health -= self.health_change_speed
            transition_width = int((self.target_health - self.current_health) / self.health_ratio)
            transition_color = (255, 255, 0)

        bar_width = int(self.current_health / self.health_ratio)
        bar_rect = pygame.Rect(self.pos[0], self.pos[1], bar_width, 12)
        transition_rect = pygame.Rect(bar_rect.right, self.pos[1], transition_width, 12)

        pygame.draw.rect(surface, (255, 0, 0), bar_rect)
        pygame.draw.rect(surface, transition_color, transition_rect)
        pygame.draw.rect(surface, (255, 255, 255), (self.pos[0], self.pos[1], self.health_bar_length, 12), 3)

        font = pygame.font.Font('Assets/Fonts/m5x7.ttf', 20)
        text_surface = font.render(self.name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midbottom=(self.pos[0] + self.health_bar_length // 2, self.pos[1] - 5))
        surface.blit(text_surface, text_rect)