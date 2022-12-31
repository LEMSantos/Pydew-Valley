from typing import Tuple, Union, List
from collections import defaultdict

import pygame
from pygame import Surface
from pygame.sprite import AbstractGroup
from pytmx.util_pygame import load_pygame
from src.core.utils import import_folder

from src.config import *
from .generic_sprite import GenericSprite


class SoilTile(GenericSprite):

    def __init__(self,
                position: Tuple[int, int],
                surface: Surface,
                groups: Union[List[AbstractGroup], AbstractGroup]):

        super().__init__(
            position=position,
            surface=surface,
            groups=groups,
            z=LAYERS["soil"],
        )


class SoilLayer:

    def __init__(self, all_sprites: pygame.sprite.Group) -> None:
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()

        self.soil_surfs = import_folder(
            f"{BASE_APP_PATH}/graphics/soil",
            get_dict=True,
        )

        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
        self.farmable_grid = defaultdict(list)

        farmable_tiles = load_pygame(
            f"{BASE_APP_PATH}/data/map.tmx"
        ).get_layer_by_name("Farmable").tiles()

        for x, y, _ in farmable_tiles:
            self.farmable_grid[(x, y)].append("F")

    def create_hit_rects(self):
        self.hit_rects = []

        for (index_col, index_row), _ in list(self.farmable_grid.items()):
            x, y = index_col * TILE_SIZE, index_row * TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x, y = rect.x // TILE_SIZE, rect.y // TILE_SIZE

                if (
                    "F" in self.farmable_grid[(x, y)]
                    and "X" not in self.farmable_grid[(x, y)]
                ):
                    self.farmable_grid[(x, y)].append("X")
                    self.create_soil_tiles()

    def create_soil_tiles(self):
        for soil in self.soil_sprites.sprites():
            soil.kill()

        for (x, y), cell in list(self.farmable_grid.items()):
            if "X" in cell:
                top = "X" in self.farmable_grid[(x, y - 1)]
                right = "X" in self.farmable_grid[(x + 1, y)]
                bottom = "X" in self.farmable_grid[(x, y + 1)]
                left = "X" in self.farmable_grid[(x - 1, y)]

                positions = [
                    ("t", top), ("r", right),
                    ("b", bottom), ("l", left),
                ]

                tile_type = "o"

                if any([top, right, bottom, left]):
                    mask = ""

                    for letter, has_adjacent in positions:
                        if has_adjacent:
                            mask = f"{mask}{letter}"

                    tile_type = f"_{mask}"

                SoilTile(
                    position=(x * TILE_SIZE, y * TILE_SIZE),
                    surface=self.soil_surfs[tile_type],
                    groups=[self.all_sprites, self.soil_sprites],
                )
