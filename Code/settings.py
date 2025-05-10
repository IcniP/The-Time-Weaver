import pygame
from pytmx.util_pygame import load_pygame

import sys
import random
import math
from abc import ABC, abstractmethod

from os import walk, listdir
from os.path import join, dirname, abspath
from pathlib import Path
import xml.etree.ElementTree as ET


# Default resolution
WINDOW_WIDTH, WINDOW_HEIGHT = 640, 360

# Tile size and framerate
TILE_SIZE = 32 
FRAMERATE = 60