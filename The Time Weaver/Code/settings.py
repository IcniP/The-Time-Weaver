import pygame
from os import walk
from os.path import join
from pytmx.util_pygame import load_pygame

# Default resolution
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 360

# Tile size and framerate
TILE_SIZE = 32 
FRAMERATE = 60
BG_COLOR = '#fcdfcd'

# Resolutions
RESOLUTIONS = {
    "normal": (640, 360),
    "2x": (1280, 720),
    "3x": (1920, 1080)
}
