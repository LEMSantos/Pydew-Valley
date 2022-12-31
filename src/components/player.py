import os
from collections import defaultdict, namedtuple
from typing import Callable, Tuple
from itertools import cycle

import pygame

from src.config import *
from src.core.utils import import_folder
from src.core.timer import Timer
from src.map.soil import SoilLayer

UseAction = namedtuple("UseAction", ["key", "timer"])
SwitchAction = namedtuple("SwitchAction", ["key", "timer", "variable", "options"])
InteractAction = namedtuple("InteractAction", ["target", "run"])
Movement = namedtuple("Movement", ["key", "direction", "value", "status"])


class Player(pygame.sprite.Sprite):

    def __init__(self,
                 position: Tuple[float, float],
                 group: pygame.sprite.Group,
                 collision_sprites: pygame.sprite.Group,
                 tree_sprites: pygame.sprite.Group,
                 interaction_sprites: pygame.sprite.Group,
                 soil_layer: SoilLayer,
                 toggle_shop: Callable) -> None:

        super().__init__(group)

        self.import_assets()

        self.status = "down_idle"
        self.frame_index = 0

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)
        self.z = LAYERS["main"]

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites

        self.timers = {
            "tool_use": Timer(350, self.use_tool),
            "seed_use": Timer(350, self.use_seed),
            "tool_switch": Timer(200),
            "seed_switch": Timer(200),
        }

        self.tools = ["hoe", "axe", "water"]
        self.tools_cycle = cycle(self.tools)
        self.selected_tool = next(self.tools_cycle)

        self.seeds = ["corn", "tomato"]
        self.seeds_cycle = cycle(self.seeds)
        self.selected_seed = next(self.seeds_cycle)

        self.item_inventory = {
            "wood": 0,
            "apple": 0,
            "corn": 0,
            "tomato": 0,
        }

        self.seed_inventory = {
            "corn": 5,
            "tomato": 5,
        }

        self.money = 200.0

        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        self.toggle_shop = toggle_shop

        self.soil_layer = soil_layer

        self.sleep = False

    def import_assets(self):
        assets_path = f"{BASE_APP_PATH}/graphics/character"

        _dirs = [
            name for name in os.listdir(assets_path)
            if os.path.isdir(f"{assets_path}/{name}")
        ]

        self.animations = defaultdict(list)

        for name in _dirs:
            self.animations[name] = import_folder(f"{assets_path}/{name}")

    def animate(self, dt: int) -> None:
        self.frame_index += 4 * dt
        self.frame_index %= len(self.animations[self.status])

        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self) -> None:
        movements = [
            Movement(key=pygame.K_UP, direction="y", value=-1, status="up"),
            Movement(key=pygame.K_DOWN, direction="y", value=1, status="down"),
            Movement(key=pygame.K_LEFT, direction="x", value=-1, status="left"),
            Movement(key=pygame.K_RIGHT, direction="x", value=1, status="right"),
        ]

        use_actions = [
            UseAction(key=pygame.K_SPACE, timer="tool_use"),
            UseAction(key=pygame.K_LCTRL, timer="seed_use"),
        ]

        switch_actions = [
            SwitchAction(key=pygame.K_q, timer="tool_switch",
                         variable="selected_tool", options=self.tools_cycle),
            SwitchAction(key=pygame.K_e, timer="seed_switch",
                         variable="selected_seed", options=self.seeds_cycle),
        ]

        interact_actions = [
            InteractAction(target="Bed", run=self.interact_with_bed),
            InteractAction(target="Trader", run=self.interact_with_trader)
        ]

        if not self.timers["tool_use"].active and not self.sleep:
            pressed_keys = pygame.key.get_pressed()

            self.direction = pygame.math.Vector2()

            for move in movements:
                if pressed_keys[move.key]:
                    setattr(self.direction, move.direction, move.value)
                    self.status = move.status

            for use_action in use_actions:
                if pressed_keys[use_action.key]:
                    self.frame_index = 0
                    self.timers[use_action.timer].activate()
                    self.direction = pygame.math.Vector2()

            for switch_action in switch_actions:
                if (
                    pressed_keys[switch_action.key]
                    and not self.timers[switch_action.timer].active
                ):
                    self.timers[switch_action.timer].activate()
                    setattr(self, switch_action.variable, next(switch_action.options))

            if pressed_keys[pygame.K_RETURN]:
                collided = pygame.sprite.spritecollide(
                    self, self.interaction_sprites, False
                )

                if collided:
                    for action in interact_actions:
                        if collided[0].name == action.target:
                            action.run()

    def get_status(self) -> None:
        if self.direction.magnitude() == 0:
            self.status = self.status.split("_")[0]
            self.status = f"{self.status}_idle"

        if self.timers["tool_use"].active:
            self.status = self.status.split("_")[0]
            self.status = f"{self.status}_{self.selected_tool}"

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, "hitbox"):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == "horizontal":
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left

                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right

                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == "vertical":
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top

                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom

                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt: int) -> None:
        normalized_direction = (
            self.direction.normalize()
            if self.direction.magnitude() > 0
            else self.direction
        )

        self.pos.x += normalized_direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision("horizontal")

        self.pos.y += normalized_direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision("vertical")

    def use_tool(self):
        if self.selected_tool == "hoe":
            self.soil_layer.get_hit(self.target_pos)

        if self.selected_tool == "axe":
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

        if self.selected_tool == "water":
            self.soil_layer.water(self.target_pos)

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[
            self.status.split("_")[0]
        ]

    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1

    def update(self, dt: int) -> None:
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()

        self.move(dt)
        self.animate(dt)

    def interact_with_bed(self):
        self.status = "left_idle"
        self.sleep = True

    def interact_with_trader(self):
        self.toggle_shop()
