# Design Notes

## Image recognition for Map image to Tile types
### First approach: image mean colour vs manually assigned colour
Compare the image's mean colour with each Tile's manually assigned colour. This worked pretty well on normal google map images.

### Second approach: image vs labelled Tile images (RGB colour histograms)
Compare the image's RGB colour histograms with each labelled Tile images'. This didn't work well at all.

### Third approach: image vs labelled Tile images (RGB pixel histograms)
Compare the image's RGB pixel histograms with each labelled Tile images'. XXXXXXXXXXX
 
### Fourth approach: image vs labelled Tile images (RGB colour clusters)
Compare the image's RGB pixel cluster with each labelled Tile images'. XXXXXXXXXXXX

### Fifth approach: image vs labelled Tile images (ML)
Compare the image's RGB pixel cluster with each labelled Tile images'. XXXXXXXXXXX
