from random import choice
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


class WaterTile(GenericSprite):

    def __init__(self,
                position: Tuple[int, int],
                surface: Surface,
                groups: Union[List[AbstractGroup], AbstractGroup]):

        super().__init__(
            position=position,
            surface=surface,
            groups=groups,
            z=LAYERS["soil water"],
        )


class SoilLayer:

    def __init__(self, all_sprites: pygame.sprite.Group, raining: bool) -> None:
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        self.raining = raining

        self.water_surfs = import_folder(f"{BASE_APP_PATH}/graphics/soil_water")
        self.soil_surfs = import_folder(
            f"{BASE_APP_PATH}/graphics/soil",
            get_dict=True,
        )

        self.create_soil_grid()
        self.create_hit_rects()

        self.watery_soils = defaultdict(lambda: False)

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

                    if self.raining:
                        self.water_all()

    def water(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x, y = rect.x // TILE_SIZE, rect.y // TILE_SIZE
                self.farmable_grid[(x, y)].append("W")

                WaterTile(
                    position=(x * TILE_SIZE, y * TILE_SIZE),
                    surface=choice(self.water_surfs),
                    groups=[self.all_sprites, self.water_sprites],
                )

    def water_all(self):
        for (index_col, index_row), cell in list(self.farmable_grid.items()):
            x, y = index_col * TILE_SIZE, index_row * TILE_SIZE

            if "X" in cell and "W" not in cell:
                cell.append("W")

                WaterTile(
                    position=(x, y),
                    surface=choice(self.water_surfs),
                    groups=[self.all_sprites, self.water_sprites],
                )

    def create_soil_tiles(self):
        for soil in self.soil_sprites.sprites():
            soil.kill()

        for (x, y), cell in list(self.farmable_grid.items()):
            position = (x * TILE_SIZE, y * TILE_SIZE)

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
                    position=position,
                    surface=self.soil_surfs[tile_type],
                    groups=[self.all_sprites, self.soil_sprites],
                )

    def remove_water(self):
        for water in self.water_sprites.sprites():
            water.kill()

        for _, cell in list(self.farmable_grid.items()):
            if "W" in cell:
                cell.remove("W")
