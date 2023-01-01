from random import random

import pygame
from pytmx.util_pygame import load_pygame

from src.config import *
from src.core.utils import *
from src.core import Transition
from src.components.menu import Menu
from src.core.particle import Particle
from src.components.player import Player
from src.components.overlay import Overlay
from src.map import (
    GenericSprite,
    Interaction,
    SoilLayer,
    Rain,
    Sky,
    MAP_LAYERS,
)


class Level:

    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()

        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.sky = Sky()
        self.rain = Rain(self.all_sprites)
        self.raining = bool(random() <= RAIN_PROBABILITY)

        self.soil_layer = SoilLayer(
            self.all_sprites,
            self.collision_sprites,
            self.raining,
        )

        self.MAP_LAYERS = MAP_LAYERS

        self.setup()

        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        self.menu = Menu(self.player, self.toggle_shop)
        self.shop_active = False

        self.success_sound = pygame.mixer.Sound(f"{BASE_APP_PATH}/audio/success.wav")
        self.success_sound.set_volume(0.1)

        self.background_music = pygame.mixer.Sound(f"{BASE_APP_PATH}/audio/music.mp3")
        self.background_music.set_volume(0.05)
        self.background_music.play(loops=-1)

    def setup(self):
        tmx_data = load_pygame(f"{BASE_APP_PATH}/data/map.tmx")

        for layer in self.MAP_LAYERS:
            if layer.object_type:
                for obj in tmx_data.get_layer_by_name(layer.name):
                    params = {
                        "position": (obj.x, obj.y),
                        "surface": obj.image,
                        "groups": [],
                    }

                    if layer.has_name:
                        params.update({"name": obj.name})

                    if layer.visible:
                        params["groups"].append(self.all_sprites)

                    if layer.collide:
                        params["groups"].append(self.collision_sprites)

                    if layer.name == "Trees":
                        params["groups"].append(self.tree_sprites)
                        params["player_add"] = self.player_add

                    layer.cls(**params)
            else:
                for x, y, surface in tmx_data.get_layer_by_name(layer.name).tiles():
                    params = {
                        "position": (x * TILE_SIZE, y * TILE_SIZE),
                        "groups": [],
                    }

                    if layer.z:
                        params.update({"z": layer.z})

                    if layer.visible:
                        params["groups"].append(self.all_sprites)

                    if layer.collide:
                        params["groups"].append(self.collision_sprites)

                    if layer.empty_surface:
                        params.update({"surface": pygame.Surface((TILE_SIZE, TILE_SIZE))})
                    elif layer.frames:
                        params.update({"frames": import_folder(layer.frames)})
                    else:
                        params.update({"surface": surface})

                    layer.cls(**params)

        for obj in tmx_data.get_layer_by_name("Player"):
            if obj.name == "Start":
                self.player = Player(
                    position=(obj.x, obj.y),
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction_sprites=self.interaction_sprites,
                    soil_layer=self.soil_layer,
                    toggle_shop=self.toggle_shop,
                )

            if obj.name in ["Bed", "Trader"]:
                Interaction(
                    position=(obj.x, obj.y),
                    size=(obj.width, obj.height),
                    groups=self.interaction_sprites,
                    name=obj.name,
                )

        GenericSprite(
            position=(0, 0),
            surface=pygame.image.load(
                f"{BASE_APP_PATH}/graphics/world/ground.png").convert_alpha(),
            groups=[self.all_sprites],
            z = LAYERS["ground"],
        )

    def player_add(self, item: str, amount: int=1):
        self.player.item_inventory[item] += amount
        self.success_sound.play()

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    def reset(self):
        self.soil_layer.update_plants()

        self.raining = bool(random() <= RAIN_PROBABILITY)

        self.soil_layer.remove_water()
        self.soil_layer.raining = self.raining

        if self.raining:
            self.soil_layer.water_all()

        self.sky.reset_sky()

        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()

            tree.create_fruit()

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type, 1)

                    plant.kill()

                    Particle(
                        position=plant.rect.topleft,
                        surface=plant.image,
                        groups=[self.all_sprites],
                        z=LAYERS["main"],
                    )

                    x = plant.rect.centerx // TILE_SIZE
                    y = plant.rect.centery // TILE_SIZE
                    self.soil_layer.farmable_grid[(x, y)].remove("P")

    def run(self, dt: int) -> None:
        self.display_surface.fill("black")
        self.all_sprites.custom_draw(self.player)

        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()

        self.overlay.display()

        if self.raining and not self.shop_active:
            self.rain.update()

        self.sky.display(dt)

        if self.player.sleep:
            self.transition.play()


class CameraGroup(pygame.sprite.Group):

    def __init__(self) -> None:
        super().__init__()

        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player: Player) -> None:
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for sprite in sorted(self.sprites(), key=lambda s: (s.z, s.rect.centery)):
            offset_rect = sprite.rect.copy()
            offset_rect.center -= self.offset

            self.display_surface.blit(sprite.image, offset_rect)
