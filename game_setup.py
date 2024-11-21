import pygame
from typing import Final

"""
 Setting up the game
 Defining vaars for the rest of the code
"""

# Core definitions
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

FRAME_RATE: Final = 60