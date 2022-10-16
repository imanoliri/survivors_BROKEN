This directory contains the maps that will be used for the game.

* .maps:
	The *.JPG files are the direct snippets from google maps. They will be ignored by the game program.
	They are either normal maps, satellite or terrain maps.

	The *.jpg files are derive from the *.JPG ones and come in different variants:
		- SQ: square maps. For a map of size 200 tiles -> 14x14 tiles
		- H: 4:3 ratio. For a map of size 200 tiles -> 12x16 tiles
		- V: 3:4 ratio. For a map of size 200 tiles -> 16x12 tiles

	Feel free to add more yourself!

* .maps/tilemaps:
	This directory stores the TileMaps and other information calculated by the game programm.
	These results will be reused by the program and if you want to get new ones, you should
	indicate it so in the related configuration file.

* .maps/example_tiles:
	Here are some labelled tiles that the game programm will use to convert images to TileMaps.
	The filenames look like "n_xxx" where "n" indicates the kind of tile and "xxx" the number
	of the example.
