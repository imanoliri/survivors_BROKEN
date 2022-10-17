"""
This is the main script to play a game of "Survivors".
"""

from cards import CardStack
from map2tiles import image_file_to_tilemap_file
import json
import pandas as pd
from os import listdir
from os.path import isfile, join
from game import play_game, add_lines_to_gamelog_and_print_them


def main():

    def start_gamelog():
        with open("game.json", "r") as fp:
            game_kwargs = json.load(fp)
        gamelog_filepath = game_kwargs["gamelog_filepath"]
        gamelog = pd.DataFrame([], columns=['event'])
        gamelog = add_lines_to_gamelog_and_print_them(
            ['<<<< Starting "survivors" >>>>'], gamelog, gamelog_filepath)
        return gamelog_filepath, gamelog

    def prepare_map(gamelog):

        # Ask for which map
        with open("map2tiles.json", "r") as fp:
            map2tiles_kwargs = json.load(fp)
        mapdir = map2tiles_kwargs['maps_directory']
        maps = [
            f for f in listdir(mapdir)
            if isfile(join(mapdir, f)) and f.endswith('.jpg')
        ]
        select_map = {m + 1: mappath for m, mappath in enumerate(maps)}
        sep = "\n\t"
        map_sel_strings = [
            f'{m}. {map_file}' for (m, map_file) in select_map.items()
        ]
        sel_map_strings = ['Select a map:'] + map_sel_strings
        gamelog = add_lines_to_gamelog_and_print_them([''] + sel_map_strings,
                                                      gamelog,
                                                      gamelog_filepath,
                                                      print_lines=False)
        selmap = int(
            input(f'Select a map:{sep}{sep.join(map_sel_strings)}{sep}--> '))

        gamelog = add_lines_to_gamelog_and_print_them([f'--> {selmap}'],
                                                      gamelog,
                                                      gamelog_filepath)

        selmap

        # Prepare chosen map
        map2tiles_kwargs['image_filepath'] = f'{mapdir}/{select_map[selmap]}'
        gamelog = add_lines_to_gamelog_and_print_them([
            '',
            'Creating tiles for the chosen map as defined in "map2tiles.json"'
        ], gamelog, gamelog_filepath)
        image_file_to_tilemap_file(**map2tiles_kwargs)
        gamelog = add_lines_to_gamelog_and_print_them([
            'Map created. You have to copy the TileMap (maps/tilemaps > excel with the same name) to the UI of "game.xlsx"!'
        ], gamelog, gamelog_filepath)

        return gamelog

    def prepare_card_stacks(gamelog):

        # Just prepare CardStacks as defined
        gamelog = add_lines_to_gamelog_and_print_them(
            ['', 'Creating card stacks as defined in "card_stacks.json"'],
            gamelog, gamelog_filepath)
        with open("card_stacks.json", "r") as fp:
            card_stack_kwargs = json.load(fp)
        card_stacks = []
        for cs_kwargs in card_stack_kwargs:
            card_stacks.append(CardStack.from_xlsx(**cs_kwargs))
        gamelog = add_lines_to_gamelog_and_print_them(['Card stacks created.'],
                                                      gamelog,
                                                      gamelog_filepath)
        return card_stacks, gamelog

    def prepare_game(gamelog):
        # Remind user to
        prepare_game_input_lines = [
            '',
            'Before starting the game, copy the "data/game.xlsx" to the folder above it.',
            'Then, open it with google drive and save it as a google spreadsheet, where all the players can play interactively.',
            'Go to "share" and make sure anyone with a link can open it.',
            'Now, write the google sheet id to "game.json">"game_spreadsheet_id".',
            'Enter to continue.'
        ]
        gamelog = add_lines_to_gamelog_and_print_them(prepare_game_input_lines,
                                                      gamelog,
                                                      gamelog_filepath)
        i = input('\n'.join(prepare_game_input_lines))
        with open("game.json", "r") as fp:
            game_kwargs = json.load(fp)

        return game_kwargs, gamelog

    gamelog_filepath, gamelog = start_gamelog()

    gamelog = prepare_map(gamelog)

    card_stacks, gamelog = prepare_card_stacks(gamelog)

    game_kwargs, gamelog = prepare_game(gamelog)

    play_game(gamelog, card_stacks, **game_kwargs)


if __name__ == "__main__":
    main()