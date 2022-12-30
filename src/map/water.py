from typing import Tuple, Union, List

from pygame import Surface
from pygame.sprite import AbstractGroup

from src.config import LAYERS
from src.map.generic_sprite import GenericSprite


class Water(GenericSprite):

    def __init__(self,
                 position: Tuple[int, int],
                 frames: List[Surface],
                 groups: Union[List[AbstractGroup], AbstractGroup]):

        self.frame_index = 0
        self.frames = frames

        super().__init__(
            position=position,
            surface=self.frames[self.frame_index],
            groups=groups,
            z=LAYERS["water"],
        )

    def animate(self, dt: int):
        self.frame_index += 5 * dt
        self.frame_index %= len(self.frames)

        self.image = self.frames[int(self.frame_index)]

    def update(self, dt: int):
        self.animate(dt)
