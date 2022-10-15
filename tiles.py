"""
This module handles Tiles for the Wasteland virtual tabletop game.
"""
from dataclasses import dataclass
import json
import math
import numpy as np
from PIL import Image
from typing import Tuple
import pandas as pd
from pathlib import Path

Tile = str
#TileMap = np.array


@dataclass
class TileMap():

    image: np.ndarray = None
    tile_number: int = None
    tile_info: pd.DataFrame = None
    tiles: np.array = None

    def __post_init__(self):
        if self.tiles is None:
            self.tiles = self.tiles_from_image()

    @property
    def tile_counts(self) -> pd.DataFrame:

        if self.tiles is None:
            raise ValueError('No defined Tiles to count in this TileMap.')
        # Counts
        counts = zip(*np.unique(self.tiles, return_counts=True))
        tile_counts = self.tile_info.copy(deep=True)
        tile_counts = tile_counts.iloc[:, 1].to_frame()
        tile_counts['count'] = 0
        for tile, count in counts:
            tile_counts.loc[tile_counts.letter == tile, 'count'] = count

        return tile_counts

    def tiles_from_image(self) -> np.array:
        image = self.image
        ratio = image.shape[1] / image.shape[0]
        x_tiles = math.floor(math.sqrt(self.tile_number * ratio))
        y_tiles = math.floor(self.tile_number / x_tiles)

        tiles = np.empty(dtype='str', shape=(y_tiles, x_tiles))
        x_resol = math.floor(image.shape[1] / x_tiles)
        y_resol = math.floor(image.shape[0] / y_tiles)
        for x in range(x_tiles):
            for y in range(y_tiles):
                img_tile = image[y * y_resol:(y + 1) * y_resol,
                                 x * x_resol:(x + 1) * x_resol]
                tiles[y, x] = self.img_rgb_2_tile(img_tile)
        return tiles

    def img_rgb_2_tile(self, image: np.array) -> Tile:
        """
        Convert the passed RGB-array to a single tile, by checking its mean color against all possible Tiles.

        Args:
            image (np.array): RGB-array.

        Returns:
            Tile: Tile corresponding to this image.
        """
        # Get the most probable classification for all pixels
        classifications = []
        for x in range(image.shape[0]):
            for y in range(image.shape[1]):
                classifications.append(self.closest_tile_for_color(image[x,
                                                                         y]))

        # Get distribution of classifications
        df_classifications = pd.Series(classifications, name='tile')
        classification_counts = df_classifications.value_counts(normalize=True,
                                                                sort=True)
        # Get tile type from classification counts
        return self.tile_from_classification_counts(classification_counts)

    def closest_tile_for_color(self, rgb: Tuple[float]) -> Tile:
        """
        Return which Tile is the closest to this color.

        Args:
            rgb (Tuple[float]): Color to evaluate.

        Returns:
            Tile: Kind of Tile corresponding to the color.
        """
        r, g, b = rgb
        diffs_and_letters = []
        for name, letter, color in self.tile_info.values:
            cr, cg, cb = color
            color_diff = math.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
            diffs_and_letters.append((color_diff, letter))
        return min(diffs_and_letters)[1]

    @staticmethod
    def tile_from_classification_counts(counts: pd.Series) -> str:
        """
        Tile will be either the top classification count.
        If the difference with the second is not so big, the Tile will be both classes at the same time.
        If the 1st and second are Water ('L') and Wood ('W'), the Tile will be a Swamp ('S')
        """
        tiles = counts.index.values
        counts = counts.values.tolist()
        tile = tiles[0]
        if len(counts):
            return tile

        rel_difference_1_2_options = abs(counts[0] - counts[1]) / counts[0]
        if rel_difference_1_2_options < 0.2:
            first_class = tiles[0]
            second_class = tiles[1]
            if first_class == 'L' and second_class == 'W':
                tile = 'S'
            else:
                tile = f'{first_class}/{second_class}'
        return tile


def image_file_to_tilemap_file(image_filepath: str, tile_info_kwargs: dict,
                               map_tile_number: int, *args, **kwargs):
    """
    This function reads a target image, which is expected to be a google maps snippet
    and saves it as a TileMap to a csv.
    """

    # Load image and tile information
    with open(image_filepath, "rb") as fp:
        img = Image.open(fp)
        img = np.array(img)
    with open(tile_info_kwargs["filepath"], 'rb') as fp:
        tile_info = pd.read_excel(fp,
                                  tile_info_kwargs["sheetname"],
                                  index_col=0)
        tile_info.color = [
            tuple(int(c) for c in color[1:-1].split(','))
            for color in tile_info.color
        ]

    # Convert image to tilemap (if not yet done)
    tilemap_filepath = f"{image_filepath.split('.')[0]}.xlsx"
    tilemap = None
    if not Path(tilemap_filepath).is_file():
        tilemap = TileMap(img, map_tile_number, tile_info)
        pd.DataFrame(tilemap.tiles).to_excel(tilemap_filepath, index=False)

    # Create and save tile counts to excel (if not yet done)
    tilemap_tile_counts_filepath = f"{image_filepath.split('.')[0]}_tile_counts.xlsx"
    if not Path(tilemap_tile_counts_filepath).is_file():
        if tilemap is None:
            tilemap = TileMap(img, map_tile_number, tile_info)
        tilemap.tile_counts.to_excel(tilemap_tile_counts_filepath, index=False)
