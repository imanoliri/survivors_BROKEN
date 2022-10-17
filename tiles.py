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
from os import listdir
from os.path import isfile, join

Tile = str


@dataclass
class TileMap():

    image: np.ndarray = None
    tile_number: int = None
    tile_info: pd.DataFrame = None
    labeled_tile_images_path: str = None

    tiles: np.ndarray = None
    tile_x_pixels: int = None
    tile_y_pixels: int = None
    labeled_tile_images: dict = None
    labeled_tile_images_colour_histograms: dict = None

    def __post_init__(self):
        if self.tiles is None:
            if self.labeled_tile_images is None and self.labeled_tile_images_path is not None:
                self.labeled_tile_images = self._load_images_from_directory(
                    self.labeled_tile_images_path)
            self.tiles = self._tiles_from_image()
            self.labeled_tile_images = None

    @staticmethod
    def _load_images_from_directory(dir: str) -> list:
        return {
            f: Image.open(f'{dir}/{f}')
            for f in listdir(dir)
            if isfile(join(dir, f)) and f.endswith('.jpg')
        }

    def _tiles_from_image(self) -> np.ndarray:
        image = self.image
        ratio = image.shape[1] / image.shape[0]
        x_tiles = math.floor(math.sqrt(self.tile_number * ratio))
        y_tiles = math.floor(self.tile_number / x_tiles)
        return self._rgb_2_tiles(image, x_tiles, y_tiles)

    def _rgb_2_tiles(self, image_rgb: np.ndarray, x_tiles: int,
                     y_tiles: int) -> np.ndarray:

        # Select rgb_2_tile function to use!
        rgb_2_tile = self._rgb_2_tile_by_closest_color
        if self.labeled_tile_images is not None:
            self.labeled_tile_images_colour_histograms = {
                fp: self._colour_histograms_from_image(np.array(img))
                for fp, img in self.labeled_tile_images.items()
            }
            rgb_2_tile = self._rgb_2_tile_by_rgb_distributions

        # Apply rgb_2_tile to all Image tiles
        tiles = (rgb_2_tile(img_tile)
                 for img_tile in self._tile_images_from_rgb(
                     image_rgb, x_tiles, y_tiles))
        return np.array(list(tiles), dtype='str').reshape(y_tiles, x_tiles)

    def _tile_images_from_rgb(self, image_rgb: np.ndarray, x_tiles: int,
                              y_tiles: int) -> Iterator[np.ndarray]:

        x_resol = math.floor(image_rgb.shape[1] / x_tiles)
        y_resol = math.floor(image_rgb.shape[0] / y_tiles)
        for x in range(x_tiles):
            for y in range(y_tiles):
                yield image_rgb[y * y_resol:(y + 1) * y_resol,
                                x * x_resol:(x + 1) * x_resol]

    def _rgb_2_tile_by_closest_color(self, image: np.ndarray) -> Tile:
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

    @staticmethod
    def _colour_histograms_from_image(img: np.array):

        def hist_to_array(counts, bins):
            return np.stack([counts, bins[1:]])

        return np.stack([
            hist_to_array(*np.histogram(colour, range=(0, 255)))
            for colour in np.moveaxis(img, 2, 0)
        ])

    def _rgb_2_tile_by_rgb_distributions(self, image: np.ndarray) -> Tile:
        tiling = pd.DataFrame([
            list(self.labeled_tile_images_colour_histograms),
            list(self.labeled_tile_images_colour_histograms.values())
        ], ['filename', 'image']).T
        tiling['difference'] = [
            self._mean_array_diference(
                self._colour_histograms_from_image(image), np.array(l_image))
            for l_image in tiling.image
        ]
        closest_tiles = tiling.loc[tiling.difference ==
                                   tiling.difference.min()]
        closest_tile_index = int(
            closest_tiles.iloc[0].filename.split('_')[0]) - 1
        return self.tile_info.iloc[closest_tile_index].letter

    @staticmethod
    def _mean_array_diference(a: np.ndarray, b: np.ndarray) -> int:
        return np.sum(np.abs(a - b)) / a.size

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
