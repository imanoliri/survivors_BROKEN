"""
This module handles Tiles for the Wasteland virtual tabletop game.
"""
import json
import math
import numpy as np
from PIL import Image
from typing import Tuple

Tile = str
TileMap = np.array


def img_rgb_2_tile(image: np.array, *args, **kwargs) -> Tile:
    """
    Convert the passed RGB-array to a single tile, by checking its mean color against all possible Tiles.

    Args:
        image (np.array): RGB-array.

    Returns:
        Tile: Tile corresponding to this image.
    """
    return closest_tile_for_color(image.mean(axis=(0, 1)), *args, **kwargs)


def closest_tile_for_color(rgb: Tuple[float], tile_info: dict) -> Tile:
    """
    Return which Tile is the closest to this color.

    Args:
        rgb (Tuple[float]): Color to evaluate.
        tile_info (dict): Tile information.

    Returns:
        Tile: Kind of Tile corresponding to the color.
    """
    r, g, b = rgb
    diffs_and_letters = []
    for letter, color in tile_info.values():
        cr, cg, cb = color
        color_diff = math.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        diffs_and_letters.append((color_diff, letter))
    return min(diffs_and_letters)[1]


def image_to_tilemap(image: np.ndarray,
                     x_tiles: int,
                     y_tiles: int,
                     tile_info_filepath: str = 'tile_info.json') -> TileMap:
    """
    This function converts the image to a TileMap.

    Args:
        image (np.ndarray): Array of RGB values of the image.
        x_tiles (int): Number of horizontal tiles to divide the map into.
        y_tiles (int): Number of vertical tiles to divide the map into.
        tile_info_filepath (str, optional): Where to load the information regarding each type of Tile.
            Defaults to 'tile_info.json'.

    Returns:
        TileMap: Converted map.
    """

    with open(tile_info_filepath, "r") as fp:
        tile_info = json.load(fp)

    # Read and fill map tiles
    tilemap = np.empty(dtype='str', shape=(x_tiles, y_tiles))
    x_resol = math.floor(image.shape[0] / x_tiles)
    y_resol = math.floor(image.shape[1] / y_tiles)
    for x in range(x_tiles):
        for y in range(y_tiles):
            img_tile = image[x * x_resol:(x + 1) * x_resol,
                             y * y_resol:(y + 1) * y_resol]
            tilemap[x, y] = img_rgb_2_tile(img_tile, tile_info)

    return tilemap


def image_file_to_tilemap_file(image_filepath: str,
                               miniature: bool = True,
                               *args,
                               **kwargs):
    """
    This function reads a target image, which is expected to be a google maps snippet
    and saves it as a TileMap to a csv.
    """

    # Load image and tile information
    with open(image_filepath, "rb") as fp:
        img = Image.open(fp)
        img = np.array(img)

    # Convert image to tilemap
    tilemap = image_to_tilemap(img, *args, **kwargs)

    # Save tilemap to csv
    np.savetxt(f"{image_filepath.split('.')[0]}.csv",
               tilemap,
               delimiter=",",
               fmt='%s')
