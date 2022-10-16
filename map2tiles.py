"""
This script reads a target image, which is expected to be a google maps snippet and translates it
to a matrix with the tiles to play Wasteland, as per the json file of the same name as this script.
"""
from tiles import TileMap
import numpy as np
from PIL import Image

import pandas as pd
from pathlib import Path

import json


def main():
    with open("map2tiles.json", "r") as fp:
        conversion_kwargs = json.load(fp)
    image_file_to_tilemap_file(**conversion_kwargs)


def image_file_to_tilemap_file(image_filepath: str, overwrite: bool,
                               map_tile_number: int, tile_info_kwargs: dict,
                               labeled_tiles_path: str, image_alpha: float,
                               *args, **kwargs):
    """
    This function reads a target image, which is expected to be a google maps snippet
    and saves it as a TileMap to a csv.
    """

    # Load image and tile information
    image, tile_info = get_image_and_tile_info(image_filepath,
                                               tile_info_kwargs)

    # Convert image to tilemap (if not yet done)
    tilemap_filepath = f"{image_filepath.split('.')[0]}.xlsx"
    tilemap_fps = tilemap_filepath.split('/')
    tilemap_fps.insert(-1, 'tilemaps')
    tilemap_filepath = '/'.join(tilemap_fps)
    Path('/'.join(tilemap_filepath.split('/')[:-1])).mkdir(parents=True,
                                                           exist_ok=True)

    tilemap = None
    if not Path(tilemap_filepath).is_file() or overwrite:
        tilemap = TileMap(image, map_tile_number, tile_info,
                          labeled_tiles_path)
        tilemap.to_excel(tilemap_filepath, image_alpha)

    # Create and save tile counts to excel (if not yet done)
    tilemap_tile_counts_filepath = f"{tilemap_filepath.split('.')[0]}_tile_counts.xlsx"
    if not Path(tilemap_tile_counts_filepath).is_file() or overwrite:
        if tilemap is None:
            tilemap = TileMap(image, map_tile_number, tile_info,
                              labeled_tiles_path)
        tilemap.tile_counts.to_excel(tilemap_tile_counts_filepath, index=False)


def get_image_and_tile_info(image_filepath: str,
                            tile_info_kwargs: dict) -> tuple:
    with open(image_filepath, "rb") as fp:
        image = Image.open(fp)
        image = np.array(image)
    with open(tile_info_kwargs["filepath"], 'rb') as fp:
        tile_info = pd.read_excel(fp,
                                  tile_info_kwargs["sheetname"],
                                  index_col=0)
        tile_info.color = [
            tuple(int(c) for c in color[1:-1].split(','))
            for color in tile_info.color
        ]
    return image, tile_info


if __name__ == "__main__":
    main()