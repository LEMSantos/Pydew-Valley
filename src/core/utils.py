import os
import pygame


def import_folder(path):
    surface_list = []

    for _, __, img_files in os.walk(path):
        for image in sorted(img_files):
            surface_list.append(
                pygame.image.load(f"{path}/{image}").convert_alpha()
            )

    return surface_list
