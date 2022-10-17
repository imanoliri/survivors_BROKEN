# Design Notes

## Image recognition for Map image to Tile types
### 1st approach: image mean colour vs manually assigned colour
Compare the image's mean colour with each Tile's manually assigned colour. This worked almost well on normal google map images.

### 2nd approach: ranking of image pixel colour vs manually assigned colour
Compare all the image's pixels' colour with each Tile's manually assigned colour.
The most common Tile is assigned to the image. This worked pretty well on normal google map images.

### 3rd approach: image vs labelled Tile images (RGB colour histograms)
Compare the image's RGB colour histograms with each labelled Tile images'. This didn't work well at all.

### 4th approach: image vs labelled Tile images (RGB pixel histograms)
Compare all the image's pixels' colour with each labeled Tile's manually assigned colour.
The most common Tile is assigned to the image. XXXXXXXXXXX

### 5th approach: image vs labelled Tile images (RGB pixel histograms)
Compare the image's RGB pixel histograms (4D) with each labelled Tile images'. This is reaaaaally slow and doesn't work!
 
### 6th approach: image vs labelled Tile images (RGB colour clusters)
Compare the image's RGB pixel cluster with each labelled Tile images'. XXXXXXXXXXXX

### 7th approach: image vs labelled Tile images (ML)
Compare the image's RGB pixel cluster with each labelled Tile images'. XXXXXXXXXXX
