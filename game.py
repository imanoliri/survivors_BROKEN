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
            *args,
            gamelog=gamelog,
            gamelog_filepath=gamelog_filepath,
            card_stacks=[event_card_stack, player_card_stack],
            **kwargs)
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
                gamelog=gamelog,
                gamelog_filepath=gamelog_filepath,
                card_stacks=[event_card_stack, player_card_stack],
                **kwargs)
            if not play:
                break

        round += 1


def game_finished(game_spreadsheet_id: str, players_sheetname: str,
                  gamelog: pd.DataFrame, gamelog_filepath: str,
                  card_stacks: List[CardStack], until_no_cards: bool, *args,
                  **kwargs) -> bool:

    url = f"https://docs.google.com/spreadsheets/d/{game_spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={players_sheetname}"
    player_data = pd.read_csv(url)

    # If playing until no cards and check victory points for winners
    if until_no_cards:
        if any(not cs.cards for cs in card_stacks):
            max_vp = max(player_data.points)
            winners = player_data.loc[player_data.points == max_vp]
            if len(winners) == 1:
                winner_lines = [
                    f'The winner by victory points is {winners.name.iloc[0]}!'
                ]
            elif len(winners) > 1:
                winner_lines = [
                    f'There is a stalemate between {", ".join(n for n in winners.name)}!',
                    'They have to agree to share the victory or no one wins.'
                ]

            lines_to_print = [
                'The game finishes because the cards are finished.'
            ] + winner_lines
            add_lines_to_gamelog_and_print_them(lines_to_print, gamelog,
                                                gamelog_filepath)
            return True

    # If 1 or less players have survivors left
    winners = player_data.loc[player_data.survivors > 0]
    if len(winners) <= 1:
        if len(winners) == 1:
            lines_to_print = [
                f'Only {winners.name.iloc[0]} remains and wins the game!'
            ]
        elif len(winners) == 0:
            lines_to_print = [
                f'All players are dead and no one wins the game...'
            ]
        add_lines_to_gamelog_and_print_them(lines_to_print, gamelog,
                                            gamelog_filepath)
        return True
    return False


def deal_card_update_and_save_gamelog(card_stack: CardStack,
                                      gamelog: pd.DataFrame,
                                      gamelog_filepath: str,
                                      premessage: str = None):
    # Deal card, update game log
    lines_to_print = card_stack.card_print_strings(card_stack.deal_card())
    if premessage:
        lines_to_print = [premessage] + lines_to_print

    add_lines_to_gamelog_and_print_them(lines_to_print, gamelog,
                                        gamelog_filepath)
    i = input('Enter to continue')

    return gamelog


def add_lines_to_gamelog_and_print_them(lines_to_print: List[str],
                                        gamelog: pd.DataFrame,
                                        gamelog_filepath: str):
    # Update gamelog
    for cprint in lines_to_print:
        gamelog = add_text_to_game_log(gamelog, cprint)

    # Save game log
    with open(gamelog_filepath, 'w') as f:
        lines = '\n'.join(gamelog.event.values.tolist())
        f.write(f'<span style="white-space: pre-line">\n{lines}</span>')

    # Print lines
    print('\n'.join(lines_to_print))


def add_text_to_game_log(gamelog: pd.DataFrame, txt: str):
    return pd.concat([gamelog, pd.DataFrame([txt], columns=['event'])],
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