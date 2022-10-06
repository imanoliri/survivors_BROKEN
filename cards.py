"""
This module deals with card stacks and other objects.
"""
from dataclasses import dataclass
from typing import List
import pandas as pd
import random


@dataclass
class CardStack():
    card_types: pd.DataFrame
    cards: List[int] = None
    dealt_cards: List[int] = None

    def __post_init__(self):
        if self.cards is None:
            self.cards = self._get_fresh_cards()
        if self.dealt_cards is None:
            self.dealt_cards = []

    def deal_card(self) -> int:
        if not self.cards:
            print(
                'All cards were already dealt! They will be reshuffled and the next will be dealt.'
            )
            self.cards = self._get_fresh_cards()
            self.dealt_cards = []
        card = self.cards.pop()
        self.dealt_cards.append(card)
        return card

    def print_card(self, card):
        cd = self.card_types.loc[card, ['name', 'description']]
        cd_print = ['\n']
        cd_print += cd.values.tolist()
        print('\n'.join(cd_print))

    def _get_fresh_cards(self):
        cards = []
        for cid, (nr, *_) in self.card_types.iterrows():
            cards += [cid] * nr
        random.shuffle(cards)
        return cards

    @classmethod
    def from_xlsx(cls, filepath: str, sheetname: str) -> 'CardStack':
        with open(filepath, 'rb') as fp:
            card_types = pd.read_excel(fp, sheetname, index_col=0)
        return cls(card_types=card_types)
