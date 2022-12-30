from typing import Tuple, Union, List

import pygame
from pygame import Surface
from pygame.sprite import AbstractGroup

from src.core.timer import Timer
from src.map.generic_sprite import GenericSprite


class Particle(GenericSprite):

    def __init__(self,
                 position: Tuple[float, float],
                 surface: Surface,
                 groups: Union[List[AbstractGroup], AbstractGroup],
                 z: int,
                 duration: int=200):

        super().__init__(position, surface, groups, z)

        self.animation_timer = Timer(duration)
        self.animation_timer.activate()

        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()

        new_surf.set_colorkey((0, 0, 0))

        self.image = new_surf

    def update(self, dt: float):
        self.animation_timer.update()

        if not self.animation_timer.active:
            self.kill()
