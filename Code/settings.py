import pygame
from os import walk
from os.path import join
from pathlib import Path
from os import listdir
from os.path import join, dirname, abspath
from pytmx.util_pygame import load_pygame
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
import random
import math

# Default resolution
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 360

# Tile size and framerate
TILE_SIZE = 32 
FRAMERATE = 60
