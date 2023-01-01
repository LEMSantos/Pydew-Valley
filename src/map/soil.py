from random import choice
from typing import Callable, Text, Tuple, Union, List
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


class Plant(pygame.sprite.Sprite):

    def __init__(self,
                soil: SoilTile,
                groups: Union[List[AbstractGroup], AbstractGroup],
                plant_type: Text,
                check_watered: Callable):

        super().__init__(groups)

        self.check_watered = check_watered

        self.plant_type = plant_type
        self.frames = import_folder(f"{BASE_APP_PATH}/graphics/fruit/{plant_type}")
        self.soil = soil

        self.grow_speed = GROW_SPEED[plant_type]
        self.max_age = len(self.frames) - 1
        self.age = 0
        self.harvestable = False

        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == "corn" else -8
        self.rect = self.image.get_rect(
            midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset)
        )

        self.z=LAYERS["ground plant"]

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed

            if self.age >= 1:
                self.z = LAYERS["main"]
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)

                # self.add()

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(
                midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset)
            )


class SoilLayer:

    def __init__(self,
                 all_sprites: pygame.sprite.Group,
                 collision_sprites: pygame.sprite.Group,
                 raining: bool) -> None:

        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        self.raining = raining

        self.water_surfs = import_folder(f"{BASE_APP_PATH}/graphics/soil_water")
        self.soil_surfs = import_folder(
            f"{BASE_APP_PATH}/graphics/soil",
            get_dict=True,
        )

        self.create_soil_grid()
        self.create_hit_rects()

        self.watery_soils = defaultdict(lambda: False)

        self.hoe_sound = pygame.mixer.Sound(f"{BASE_APP_PATH}/audio/hoe.wav")
        self.water_sound = pygame.mixer.Sound(f"{BASE_APP_PATH}/audio/water.mp3")
        self.plant_sound = pygame.mixer.Sound(f"{BASE_APP_PATH}/audio/plant.wav")

        self.hoe_sound.set_volume(0.1)
        self.water_sound.set_volume(0.1)
        self.plant_sound.set_volume(0.1)

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
                self.hoe_sound.play()

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
        self.water_sound.play()

        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x, y = rect.x // TILE_SIZE, rect.y // TILE_SIZE
                cell = self.farmable_grid[(x, y)]

                if "X" in cell and "W" not in cell:
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

    def check_watered(self, position):
        x, y = position[0] // TILE_SIZE, position[1] // TILE_SIZE
        cell = self.farmable_grid[(x, y)]

        return "W" in cell

    def plant_seed(self, point, seed: Text):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                self.plant_sound.play()

                x, y = soil_sprite.rect.x // TILE_SIZE, soil_sprite.rect.y // TILE_SIZE

                if "P" not in self.farmable_grid[(x, y)]:
                    self.farmable_grid[(x, y)].append("P")

                    Plant(
                        soil=soil_sprite,
                        groups=[
                            self.all_sprites,
                            self.plant_sprites,
                            self.collision_sprites,
                        ],
                        plant_type=seed.lower(),
                        check_watered=self.check_watered
                    )

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()
