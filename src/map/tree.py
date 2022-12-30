from random import random, choice
from typing import Callable, Tuple, Union, List, Text

import pygame
from pygame import Surface
from pygame.sprite import AbstractGroup

from src.core.timer import Timer
from src.core.particle import Particle
from src.map.generic_sprite import GenericSprite
from src.config import BASE_APP_PATH, APPLE_POS, LAYERS


class Tree(GenericSprite):

    def __init__(self,
                 position: Tuple[int, int],
                 surface: Surface,
                 groups: Union[List[AbstractGroup], AbstractGroup],
                 name: Text,
                 player_add: Callable):

        super().__init__(position, surface, groups)

        self.health = 5
        self._alive = True
        self.wood_amount = 1 if name.lower() == "small" else 2
        self.stump_surf = pygame.image.load(
            f"{BASE_APP_PATH}/graphics/stumps/{name.lower()}.png"
        ).convert_alpha()

        self.invulnerable_timer = Timer(200)

        self.apple_surf = pygame.image.load(f"{BASE_APP_PATH}/graphics/fruit/apple.png")
        self.apple_position = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()

        self.create_fruit()

        self.player_add = player_add

    def damage(self):
        self.health -= 1

        apple_sprites = self.apple_sprites.sprites()

        if len(apple_sprites) > 0:
            random_apple = choice(apple_sprites)

            Particle(
                position=random_apple.rect.topleft,
                surface=random_apple.image,
                groups=random_apple.groups(),
                z=random_apple.z,
            )

            random_apple.kill()

            self.player_add("apple")

    def check_death(self):
        if self.health <= 0:
            Particle(
                position=self.rect.topleft,
                surface=self.image,
                groups=self.groups(),
                z=LAYERS["fruit"],
                duration=300
            )

            self._alive = False

            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)

            self.player_add("wood", self.wood_amount)

    def create_fruit(self):
        if self._alive:
            for position in self.apple_position:
                if random() < 0.2:
                    x = self.rect.left + position[0]
                    y = self.rect.top + position[1]

                    GenericSprite(
                        position=(x, y),
                        surface=self.apple_surf,
                        groups=[self.groups()[0], self.apple_sprites],
                        z=LAYERS["fruit"],
                    )

    def update(self, dt):
        if self._alive:
            self.check_death()
