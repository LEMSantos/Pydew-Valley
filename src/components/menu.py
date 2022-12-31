from copy import deepcopy

import pygame

from src.config import *
from src.components.player import Player
from src.core.timer import Timer


class Menu:

    def __init__(self, player: Player, toggle_menu: bool):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(f"{BASE_APP_PATH}/font/LycheeSoda.ttf", 30)

        self.player = player
        self.toggle_menu = toggle_menu

        self.width = 500
        self.gap = 10
        self.padding = 8

        self.options = deepcopy(MENU_OPTIONS)

        self.setup()

        self.menu_index = 0
        self.menu_side = 'S'

        self.press_key_timer = Timer(200)

    def display_money(self):
        text_surf = self.font.render(f"R$ {self.player.money:.2f}", False, "Black")
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))

        pygame.draw.rect(self.display_surface, "White", text_rect.inflate(20, 10), 0, 6)
        self.display_surface.blit(text_surf, text_rect)

    def show_entry(self, text_surf, amount, left, top, cell_size, selected):
        bg_rect = pygame.Rect(
            left, top, cell_size, text_surf.get_height() + (self.padding * 2)
        )
        pygame.draw.rect(self.display_surface, "White", bg_rect, 0, 6)

        text_rect = text_surf.get_rect(midleft=(left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        amount_surf = self.font.render(f"{amount}", False, "Black")
        amount_rect = amount_surf.get_rect(midright=(bg_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        if selected:
            pygame.draw.rect(self.display_surface, "Red", bg_rect, 4, 6)

    def display_options(self):
        cell_size = (self.width - self.gap) / 2

        sell_rect = self.sell_text.get_rect(
            center=(self.menu_left + self.gap + cell_size // 2, self.menu_top - 40)
        )
        buy_rect = self.buy_text.get_rect(
            center=(self.menu_left + self.gap + cell_size * 1.5, self.menu_top - 40)
        )

        self.display_surface.blit(self.sell_text, sell_rect)
        self.display_surface.blit(self.buy_text, buy_rect)

        for index, (key, option) in enumerate(list(self.sell_options.items())):
            amount = self.player.item_inventory[key]

            self.show_entry(
                option["surface"], amount,
                self.menu_left,
                self.menu_top + (
                    index * (option["surface"].get_height() + (self.padding * 2) + self.gap)
                ),
                cell_size,
                self.menu_side == "S" and index == self.menu_index
            )

        for index, (key, option) in enumerate(list(self.buy_options.items())):
            amount = self.player.seed_inventory[key]

            self.show_entry(
                option["surface"], amount,
                self.menu_left + cell_size + self.gap,
                self.menu_top + (
                    index * (option["surface"].get_height() + (self.padding * 2) + self.gap)
                ),
                cell_size,
                self.menu_side == "B" and index == self.menu_index
            )

    def setup(self):
        self.buy_options = {}
        self.sell_options = {}
        self.total_height = 0

        for key, value in self.options.items():
            value["surface"] = self.font.render(value["name"], False, "Black", "White")

            if value["buy"]:
                self.buy_options[key] = value

            if value["sell"]:
                self.sell_options[key] = value

            self.total_height += value["surface"].get_height() + (self.padding * 2)

        self.total_height += self.gap * (len(self.options) - 1)

        self.menu_top = (SCREEN_HEIGHT - self.total_height) / 2
        self.menu_left = (SCREEN_WIDTH - self.width) / 2
        self.main_rect = pygame.Rect(
            self.menu_left, self.menu_top, self.width, self.total_height
        )

        self.sell_text = self.font.render("Vender", False, "Blue", "White")
        self.buy_text = self.font.render("Comprar", False, "Red", "White")

    def input(self):
        pressed_keys = pygame.key.get_pressed()
        self.press_key_timer.update()

        if pressed_keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.press_key_timer.active:
            if pressed_keys[pygame.K_LEFT]:
                self.press_key_timer.activate()

                self.menu_index = 0
                self.menu_side = "S"

            if pressed_keys[pygame.K_RIGHT]:
                self.press_key_timer.activate()

                self.menu_index = 0
                self.menu_side = "B"

            if pressed_keys[pygame.K_DOWN]:
                self.press_key_timer.activate()

                self.menu_index += 1

                if self.menu_side == "S":
                    options_len = len(self.sell_options)
                else:
                    options_len = len(self.buy_options)

                if self.menu_index >= options_len:
                    self.menu_index = options_len - 1

            if pressed_keys[pygame.K_UP]:
                self.press_key_timer.activate()

                self.menu_index -= 1

                if self.menu_index < 0:
                    self.menu_index = 0

            if pressed_keys[pygame.K_SPACE]:
                self.press_key_timer.activate()

                if self.menu_side == "S":
                    selected = list(self.sell_options.keys())[self.menu_index]

                    if self.player.item_inventory[selected] > 0:
                        self.player.item_inventory[selected] -= 1
                        self.player.money += SALE_PRICES[selected]
                else:
                    selected = list(self.buy_options.keys())[self.menu_index]

                    if self.player.money >= PURCHASE_PRICES[selected]:
                        self.player.seed_inventory[selected] += 1
                        self.player.money -= PURCHASE_PRICES[selected]

    def update(self):
        self.input()
        self.display_money()
        self.display_options()
