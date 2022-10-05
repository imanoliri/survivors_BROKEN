"""
This script reads a target image, which is expected to be a google maps snippet and translates it
to a matrix with the tiles to play Wasteland, as per the json file of the same name as this script.
"""

from tiles import image_file_to_tilemap_file
import json


def main():
    with open("map2tiles.json", "r") as fp:
        conversion_kwargs = json.load(fp)
    image_file_to_tilemap_file(**conversion_kwargs)


if __name__ == "__main__":
    main()