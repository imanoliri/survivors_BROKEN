"""
This script loads the card dealers, as per the json file of the same name as this script
and deals all their cards until empty.
"""

from cards import CardStack
import json


def main():

    # Load CardStack configuration and create all CardStacks
    with open("card_stacks.json", "r") as fp:
        card_stack_kwargs = json.load(fp)
    card_stacks = []
    for cs_kwargs in card_stack_kwargs:
        card_stacks.append(CardStack.from_xlsx(**cs_kwargs))

    # Deal all CardStack objects in parallel until empty
    card_stacks_to_deal = card_stacks
    while True:
        if not card_stacks_to_deal:
            break
        for cs in card_stacks_to_deal:
            if not cs.cards:
                card_stacks_to_deal.remove(cs)
                continue
            card = cs.deal_card()
            cs.print_card(card)


if __name__ == "__main__":
    main()