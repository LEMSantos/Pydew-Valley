import os
import pygame


def import_folder(path, get_dict=False):
    def __handle_dict(surfaces, name, surf):
        surfaces[name] = surf

    def __handle_list(surfaces, _, surf):
        surfaces.append(surf)

    surfaces, handle_add = (
        ({}, __handle_dict)
        if get_dict else ([], __handle_list)
    )

    for _, __, img_files in os.walk(path):
        for image in sorted(img_files):
            handle_add(
                surfaces,
                image.replace(".png", ""),
                pygame.image.load(f"{path}/{image}").convert_alpha()
            )

    return surfaces
