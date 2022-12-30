from typing import Tuple, Union, List, Text

from pygame import Surface
from pygame.sprite import AbstractGroup

from src.map.generic_sprite import GenericSprite


class Interaction(GenericSprite):

    def __init__(self,
                 position: Tuple[int, int],
                 size: Tuple[float, float],
                 groups: Union[List[AbstractGroup], AbstractGroup],
                 name: Text):

        super().__init__(position, Surface(size), groups)
        self.name = name
