import sys

import pygame

from src.config import *
from src.level import Level


class Game:

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.level = Level()

        pygame.display.set_caption(GAME_TITLE)

    def __handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def run(self) -> None:
        while True:
            self.__handle_events()

            dt = self.clock.tick() / 1000
            self.level.run(dt)

            pygame.display.update()
