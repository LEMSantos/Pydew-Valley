from typing import Tuple, Union, List

from pygame import Surface
from pygame.sprite import Sprite, AbstractGroup

from src.config import LAYERS


class GenericSprite(Sprite):

    def __init__(self,
                position: Tuple[int, int],
                surface: Surface,
                groups: Union[List[AbstractGroup], AbstractGroup],
                z: int = LAYERS["main"]):

        super().__init__(groups)

        self.image = surface
        self.rect = surface.get_rect(topleft=position)
        self.hitbox = self.rect.copy().inflate(
            -self.rect.width * 0.2,
            -self.rect.height * 0.75,
        )

        self.z = z
