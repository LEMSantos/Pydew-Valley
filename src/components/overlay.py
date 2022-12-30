import pygame

from src.config import *
from src.components.player import Player


class Overlay:

    def __init__(self, player: Player):
        self.display_surface = pygame.display.get_surface()
        self.player = player

        self.tools_surf = self.import_assets(player.tools)
        self.seeds_surf = self.import_assets(player.seeds)

    def import_assets(self, files):
        assets_path = f"{BASE_APP_PATH}/graphics/overlay"

        return {
            file: pygame.image.load(f"{assets_path}/{file}.png").convert_alpha()
            for file in files
        }

    def display(self):
        tool_surf = self.tools_surf[self.player.selected_tool]
        seed_surf = self.seeds_surf[self.player.selected_seed]

        tool_rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS["tool"])
        seed_rect = seed_surf.get_rect(midbottom=OVERLAY_POSITIONS["seed"])

        self.display_surface.blit(tool_surf, tool_rect)
        self.display_surface.blit(seed_surf, seed_rect)
