"""
This script plays a game, as per the json file of the same name.
"""

from cards import CardStack
from tiles import image_file_to_tilemap_file
import json
import pandas as pd
from typing import List


def play_game(card_stacks: List[CardStack], gamelog_filepath: str,
              players: int, *args, **kwargs):

    # Define CardStacks and start with clean gamelog
    event_card_stack, player_card_stack = card_stacks
    gamelog = pd.DataFrame([], columns=['event'])

    # Rounds loop
    play = True
    round = 1
    while play:
        gamelog = deal_card_update_and_save_gamelog(
            event_card_stack,
            gamelog,
            gamelog_filepath,
            premessage=f'\n------ Turn {round} ------')

        play = not game_finished(
            *args, card_stacks=[event_card_stack, player_card_stack], **kwargs)
        if not play:
            break

        # Turns loop
        for player in range(1, players + 1):
            gamelog = deal_card_update_and_save_gamelog(
                player_card_stack,
                gamelog,
                gamelog_filepath,
                premessage=f'\n> Player {player}')

            play = not game_finished(
                *args,
                card_stacks=[event_card_stack, player_card_stack],
                **kwargs)
            if not play:
                break

        round += 1


def game_finished(game_excel_filepath: str, players_sheetname: str,
                  card_stacks: List[CardStack], until_no_cards: bool, *args,
                  **kwargs) -> bool:

    # If playing until no cards and any CardStack is empty
    if until_no_cards:
        if any(not cs.cards for cs in card_stacks):
            return True

    # If 1 or less players have survivors left
    player_data = pd.read_excel(game_excel_filepath, players_sheetname)
    if sum(s > 0 for s in player_data.survivors) <= 1:
        return True
    return False


def deal_card_update_and_save_gamelog(card_stack: CardStack,
                                      gl: pd.DataFrame,
                                      gamelog_filepath: str,
                                      premessage: str = None):
    # Deal card, update game log
    lines_to_print = card_stack.card_print_strings(card_stack.deal_card())
    if premessage:
        lines_to_print = [premessage] + lines_to_print
    for cprint in lines_to_print:
        gl = add_text_to_game_log(gl, cprint)

    # Save game log
    with open(gamelog_filepath, 'w') as f:
        lines = '\n'.join(gl.event.values.tolist())
        f.write(f'<span style="white-space: pre-line">\n{lines}</span>')

    # Print card and wait for response
    print('\n'.join(lines_to_print))
    i = input('Enter to continue')

    return gl


def add_text_to_game_log(gl: pd.DataFrame, txt: str):
    return pd.concat([gl, pd.DataFrame([txt], columns=['event'])],
                     axis=0,
                     ignore_index=True)


def main():

    # Read map from google maps image and write to local file
    with open("map2tiles.json", "r") as fp:
        conversion_kwargs = json.load(fp)
    image_file_to_tilemap_file(**conversion_kwargs)

    # Load all CardStacks
    with open("card_stacks.json", "r") as fp:
        card_stack_kwargs = json.load(fp)
    card_stacks = []
    for cs_kwargs in card_stack_kwargs:
        card_stacks.append(CardStack.from_xlsx(**cs_kwargs))

    # Play game
    with open("game.json", "r") as fp:
        game_kwargs = json.load(fp)
    play_game(card_stacks, **game_kwargs)


if __name__ == "__main__":
    main()