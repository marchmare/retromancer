from bpy.app.handlers import persistent
import bpy
import numpy as np
from typing import List

_DATANAME_PREF = ".retromancer_"

MAPS = {
    "bayer_2x2": [
        [0.00, 0.50],
        [0.75, 0.25],
    ],
    "bayer_4x4": [
        [0.000, 0.500, 0.125, 0.625],
        [0.750, 0.250, 0.875, 0.375],
        [0.187, 0.687, 0.062, 0.562],
        [0.937, 0.437, 0.812, 0.312],
    ],
    "bayer_8x8": [
        [0.0000, 0.5000, 0.1250, 0.6250, 0.0312, 0.5312, 0.1562, 0.6562],
        [0.7500, 0.2500, 0.8750, 0.3750, 0.7812, 0.2812, 0.9062, 0.4062],
        [0.1875, 0.6875, 0.0625, 0.5625, 0.2188, 0.7188, 0.0938, 0.5938],
        [0.9375, 0.4375, 0.8125, 0.3125, 0.9688, 0.4688, 0.8438, 0.3438],
        [0.0469, 0.5469, 0.1719, 0.6719, 0.0156, 0.5156, 0.1406, 0.6406],
        [0.7969, 0.2969, 0.9219, 0.4219, 0.7656, 0.2656, 0.8906, 0.3906],
        [0.2344, 0.7344, 0.1094, 0.6094, 0.2031, 0.7031, 0.0781, 0.5781],
        [0.9844, 0.4844, 0.8594, 0.3594, 0.9531, 0.4531, 0.8281, 0.3281],
    ],
}
"""Bayer ordered dither precalculated threshold maps dictionary."""


threshold_enum_items = [
    (f"{_DATANAME_PREF}{key}", f"Bayer {key.split('_')[1]} pattern", "", i + 1)
    for i, key in enumerate(MAPS.keys())
]


class ResolutionState:
    """Resolution values state tracking class."""

    current_x: int = 0
    current_y: int = 0

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(ResolutionState, cls).__new__(cls)
        return cls._instance

    @classmethod
    def update(cls, scene) -> bool:
        """
        Check if scene render resolution values changed compared to saved state.
        If they did, update the state. Returns boolean from the check.
        """
        if any(
            [
                cls.current_x != int(scene.render.resolution_x),
                cls.current_y != int(scene.render.resolution_y),
            ]
        ):
            cls.current_x = scene.render.resolution_x
            cls.current_y = scene.render.resolution_y
            return True
        return False


@persistent
def regenerate_textures(scene, depsgraph) -> None:
    """Regenerate all Bayer textures if the render resolution has changed."""
    if not scene.retromancer.auto_resize:
        return
    if not ResolutionState.update(scene):
        return
    if check_textures_updated(scene):
        return

    res_x = scene.render.resolution_x
    res_y = scene.render.resolution_y

    for name, map_array in MAPS.items():
        try:
            bl_image = bpy.data.images.get(f"{_DATANAME_PREF}{name}")
            bl_image.scale(res_x, res_y)
            pixel_data = generate_tiled_pixel_data(map_array, res_x, res_y)
            bl_image.pixels.foreach_set(pixel_data.ravel())
            bl_image.update()
        except AttributeError:
            pass


def generate_tiled_pixel_data(
    tmap: List[List[float]], width: int, height: int
) -> np.ndarray:
    """
    Generate an RGBA image array by tiling a given 2D threshold map across a specified width and height.
    """
    map_array = np.array(tmap)
    image_array = np.tile(
        map_array, (width // map_array.shape[0] + 1, height // map_array.shape[0] + 1)
    )[:width, :height]
    image_array = np.rot90(image_array)
    pixel_data = np.ones((height, width, 4), "f")
    pixel_data[:, :, :3] *= image_array[:, :, np.newaxis]
    return pixel_data


def _initialize_texture(name: str) -> bpy.types.Texture:
    """
    Get Texture data-block of specified name.
    Create new one if it doesn't exist.
    """
    T = bpy.data.textures
    texture = T.get(f"{_DATANAME_PREF}{name}", None)
    if not texture:
        texture = T.new(f"{_DATANAME_PREF}{name}", type="IMAGE")
    texture.use_fake_user = True
    return texture


def _initialize_image(name: str) -> bpy.types.Image:
    """
    Get Image data-block of specified name.
    Create new one if it doesn't exist.
    """
    I = bpy.data.images
    image = I.get(f"{_DATANAME_PREF}{name}")
    if not image:
        image = I.new(f"{_DATANAME_PREF}{name}", 0, 0)
    image.use_fake_user = True
    return image


def initialize_textures() -> None:
    """Prepare tied Image and Texture data-blocks for each Bayer matrix."""
    for treshmap in MAPS.keys():
        image = _initialize_image(treshmap)
        texture = _initialize_texture(treshmap)
        texture.image = image


def check_textures_updated(scene) -> bool:
    for treshmap in MAPS.keys():
        bl_image = bpy.data.images.get(f"{_DATANAME_PREF}{treshmap}")
        if bl_image and not bl_image.size == (
            scene.render.resolution_x,
            scene.render.resolution_y,
        ):
            return False
    return True
