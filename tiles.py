"""
This module handles Tiles for the Wasteland virtual tabletop game.
"""
from dataclasses import dataclass
import math
import numpy as np
from PIL import Image
from typing import Iterator, Tuple
import pandas as pd
from pathlib import Path
import os

Tile = str


@dataclass
class TileMap():

    image: np.ndarray = None
    tile_number: int = None
    tile_info: pd.DataFrame = None
    tiles: np.ndarray = None
    tile_x_pixels: int = None
    tile_y_pixels: int = None

    def __post_init__(self):
        if self.tiles is None:
            self.tiles = self._tiles_from_image()

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

    def tile_images(self) -> Iterator:
        return (Image.fromarray(x) for x in self.tile_rgbs())

    def tile_rgbs(self) -> Iterator[np.ndarray]:
        return (
            x
            for x in self._tile_images_from_rgb(self.image, *self.tiles.shape))

    def _tile_images_from_rgb(self, image_rgb: np.ndarray, x_tiles: int,
                              y_tiles: int) -> Iterator[np.ndarray]:

        x_resol = math.floor(image_rgb.shape[1] / x_tiles)
        y_resol = math.floor(image_rgb.shape[0] / y_tiles)
        for x in range(x_tiles):
            for y in range(y_tiles):
                yield image_rgb[y * y_resol:(y + 1) * y_resol,
                                x * x_resol:(x + 1) * x_resol]

    def _tiles_from_image(self) -> np.ndarray:
        image = self.image
        ratio = image.shape[1] / image.shape[0]
        x_tiles = math.floor(math.sqrt(self.tile_number * ratio))
        y_tiles = math.floor(self.tile_number / x_tiles)
        return self._rgb_2_tiles(image, x_tiles, y_tiles)

    def _rgb_2_tiles(self, image_rgb: np.ndarray, x_tiles: int,
                     y_tiles: int) -> np.ndarray:
        tiles = (self._img_rgb_2_tile(img_tile)
                 for img_tile in self._tile_images_from_rgb(
                     image_rgb, x_tiles, y_tiles))
        return np.array(list(tiles), dtype='str').reshape(y_tiles, x_tiles)

    def _img_rgb_2_tile(self, image: np.ndarray) -> Tile:
        """
        Convert the passed RGB-array to a single tile, by checking its mean color against all possible Tiles.

        Args:
            image (np.ndarray): RGB-array.

        Returns:
            Tile: Tile corresponding to this image.
        """
        # Get the most probable classification for all pixels
        classifications = []
        for x in range(image.shape[0]):
            for y in range(image.shape[1]):
                classifications.append(
                    self._closest_tile_for_color(image[x, y]))

        # Get distribution of classifications
        df_classifications = pd.Series(classifications, name='tile')
        classification_counts = df_classifications.value_counts(normalize=True,
                                                                sort=True)
        # Get tile type from classification counts
        return self._tile_from_classification_counts(classification_counts)

    def _closest_tile_for_color(self, rgb: Tuple[float]) -> Tile:
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
    def _tile_from_classification_counts(counts: pd.Series) -> str:
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

    def to_excel(self, fp: str, image_alpha: float = 0.7):
        sheet_name = 'map'
        df_tiles = pd.DataFrame(self.tiles)

        # Tiles to excel
        with pd.ExcelWriter(fp, engine='xlsxwriter') as writer:
            df_tiles.to_excel(writer,
                              sheet_name=sheet_name,
                              index=False,
                              header=False)

            # Adjust cell width, height and text center align
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            cell_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter'
            })
            worksheet.set_column_pixels(0, self.tiles.shape[1],
                                        self.tile_x_pixels, cell_format)
            for r in range(self.tiles.shape[0]):
                worksheet.set_row_pixels(r, self.tile_y_pixels, cell_format)

            # Add image with alpha over tiles
            alpha_image_filepath = f'{fp[:-5]}_alpha.png'
            image = Image.fromarray(self.image)
            image_rgba = image.convert("RGBA")
            image_rgba.putalpha(int(image_alpha * 255))
            image_rgba.save(alpha_image_filepath)
            worksheet.insert_image('A1', alpha_image_filepath)
        os.remove(alpha_image_filepath)

    def save_tile_images(self, directory: str, filename: str):

        for i, tile_img in enumerate(self.tile_images()):
            imag_str = f'{directory}/{filename}_{i}.jpg'
            Path(imag_str).mkdir(parents=True, exist_ok=True)
            tile_img.save(imag_str)


def image_file_to_tilemap_file(image_filepath: str, overwrite: bool,
                               map_tile_number: int, tile_info_kwargs: dict,
                               image_alpha: float, *args, **kwargs):
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
        tilemap = TileMap(image, map_tile_number, tile_info)
        tilemap.to_excel(tilemap_filepath, image_alpha)

    # Create and save tile counts to excel (if not yet done)
    tilemap_tile_counts_filepath = f"{tilemap_filepath.split('.')[0]}_tile_counts.xlsx"
    if not Path(tilemap_tile_counts_filepath).is_file() or overwrite:
        if tilemap is None:
            tilemap = TileMap(image, map_tile_number, tile_info)
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