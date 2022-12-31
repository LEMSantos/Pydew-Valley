from typing import Union, Tuple, List
from random import randint, choice

import pygame
from pygame import Surface
from pygame.sprite import AbstractGroup

from src.config import *
from src.core.timer import Timer
from src.core.utils import import_folder
from .generic_sprite import GenericSprite


class Drop(GenericSprite):

    def __init__(self,
                position: Tuple[int, int],
                surface: Surface,
                groups: Union[List[AbstractGroup], AbstractGroup],
                z: int,
                moving: bool):

        super().__init__(position, surface, groups, z)

        self.lifetime = randint(400, 500)
        self.animation_timer = Timer(self.lifetime)
        self.animation_timer.activate()

        self.moving = moving

        if moving:
            self.position = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, dt: float):
        if self.moving:
            self.position += self.direction * self.speed * dt
            self.rect.topleft = (round(self.position.x), round(self.position.y))

        self.animation_timer.update()

        if not self.animation_timer.active:
            self.kill()


class Rain:

    def __init__(self, all_sprites: pygame.sprite.Group) -> None:
        self.all_sprites = all_sprites

        self.rain_drops = import_folder(f"{BASE_APP_PATH}/graphics/rain/drops")
        self.rain_floor = import_folder(f"{BASE_APP_PATH}/graphics/rain/floor")

        self.floor_w, self.floor_h = pygame.image.load(
            f"{BASE_APP_PATH}/graphics/world/ground.png"
        ).get_size()

    def create_floor(self):
        Drop(
            position=(randint(0, self.floor_w), randint(0, self.floor_h)),
            surface=choice(self.rain_floor),
            groups=[self.all_sprites],
            z=LAYERS["rain floor"],
            moving=False,
        )

    def create_drops(self):
        Drop(
            position=(randint(0, self.floor_w), randint(0, self.floor_h)),
            surface=choice(self.rain_drops),
            groups=[self.all_sprites],
            z=LAYERS["rain drops"],
            moving=True,
        )

    def update(self):
        self.create_floor()
        self.create_drops()
