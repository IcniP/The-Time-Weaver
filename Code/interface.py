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