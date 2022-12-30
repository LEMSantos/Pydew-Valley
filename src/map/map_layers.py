from typing import Union, List
from dataclasses import dataclass

from pygame import Surface

from src.config import BASE_APP_PATH, LAYERS
from src.map import GenericSprite, Water, WildFlower, Tree


@dataclass
class MapLayer:
    name: str
    cls: GenericSprite = GenericSprite
    z: Union[int, None] =  None
    frames: Union[List[Surface], None] = None
    object_type: bool = False
    has_name: bool = False
    collide: bool = False
    visible: bool = True
    empty_surface: bool = False


MAP_LAYERS = [
    MapLayer(name="Water", cls=Water, frames=f"{BASE_APP_PATH}/graphics/water"),
    MapLayer(name="HouseFloor", z=LAYERS["house bottom"]),
    MapLayer(name="HouseFurnitureBottom", z=LAYERS["house bottom"]),
    MapLayer(name="Decoration", cls=WildFlower, object_type=True, collide=True),
    MapLayer(name="Trees", cls=Tree, object_type=True, has_name=True, collide=True),
    MapLayer(name="HouseWalls"),
    MapLayer(name="HouseFurnitureTop"),
    MapLayer(name="Fence", collide=True),
    MapLayer(name="Collision", visible=False, collide=True),
]
