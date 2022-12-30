from typing import Tuple, Union, List

from pygame import Surface
from pygame.sprite import AbstractGroup

from src.map.generic_sprite import GenericSprite


class WildFlower(GenericSprite):

    def __init__(self,
                 position: Tuple[int, int],
                 surface: Surface,
                 groups: Union[List[AbstractGroup], AbstractGroup]):

        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)
