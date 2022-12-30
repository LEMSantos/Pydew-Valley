from typing import Callable

import pygame

from src.config import *
from src.components.player import Player


class Transition:

    def __init__(self, reset_func: Callable, player: Player):
        self.display_surface = pygame.display.get_surface()

        self.reset_func = reset_func
        self.player = player

        self.overlay_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):
        self.color += self.speed

        if self.color <= 0:
            self.color = 0
            self.speed *= -1
            self.reset_func()

        if self.color > 255:
            self.color = 255
            self.player.sleep = False
            self.speed = -2

        self.overlay_image.fill((self.color, self.color, self.color))

        self.display_surface.blit(
            self.overlay_image,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
