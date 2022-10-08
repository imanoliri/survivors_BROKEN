# Survivors
The party survival board and card game

"Survivors"" is a board and card game where each player leads a party of survivors with the objective to survive the apocalypse, whether it be via cooperation or competition with each other. The final goal is to be either the last party standing or have the biggest party when the cards run out. \
The positive aspect of cooperation is specialization and more efficient use of resources (economies of scale) and the positive aspect of competition is to gain control over limited resources. \
The game is played either on a map read from a google map, a randomly generated map (Catan-style) or each player pulls out a tile and lays it each turn (Carcassone-style).

## The game loop
### Game
1. Generate map
2. Lay bases
3. Play rounds and turns until end of the game

The game can end in three ways:
1.	only one player is remaining (winner)
2.	all are dead simultaneously, for example because of an event card (no winners)
3.	the cards are finished (winner is the one with the most survivors. In case of a draw players can agree to both win or none of them)

#### Round:
1.	(Pull and play event card)
2.	Each player plays its turn
3.	(zombies play their turn)
4.	(radiation plays its turn)

#### Turn:
1.	Declare how many survivors will be scavengers this turn
2.	Pull player card
3.	(if card was map feature, place it)
4.	Resource production
5.	Resource consumption
6.	Activity

### Resources
Resources are first produced (usually by buildings or survivors assigned to a task) and then consumed (by survivors eating food and water, wounded survivors consuming medical supplies or by buildings or survivors assigned to a task). If you don’t have enough food or water for your survivors this turn, you will have to sacrifice one.
### Activities
You can perform one activity per each 3 survivors (that aren’t active scavengers), rounding up:
- Build: costs in building card. 3 survivors will be attached to this activity and cannot be used for another. If you don’t have tools for all 3, the building will take 2 turns to complete. You cannot actively use the building the same turn it’s finished.
- Gather: each tile yields a certain amount of resources you can gather directly or using a building (see the “info.xlsx” excel).
- Create/disband attack party (no activity cost)
- Move attack party: 5 tiles per turn. If you move into another party you can attack it without any activity cost. The other player can choose to trigger the combat, even if it’s not their turn. Same rules apply to player bases.
- Attack another party: it can be another attack party and then a fight will be triggered. If you attack a player’s base or building, a combat with its inhabitants/workers (in case of a base, it’s all the players idle survivors) is triggered. If you win that building can be either destroyed or put under your control.
- Trade: you can interchange resources with another player. If the player’s base or nearest outpost or attack party is farther away than 10 tiles, this takes 2 activity points.

### Combat
A combat is always between two groups of survivors and is resolved risk-style (3 dice for the attacker, 2 for the defender. If the combat is on open ground, both sides use 3 dice and equal numbers mean both loose a survivor). If a combat takes more than 10 dice throws, it will be continued in the next turn. Repeat as many times as necessary. \
Players can have weapons and other equipment on their side which will add +1 to a die (these bonuses will be as equally spread as possible). Defenders can have defenses, which add +1 to all their dice. \
Players can play combat cards at any time and can choose to finish the combat at any time. One can always try to flee (1D6<2 he loses the number of survivors on the die). Defenders in a base cannot flee. \
One weapon for each side is broken at the end of the fight. If one side was killed, the remaining weapons that were played now belong to the winner.






