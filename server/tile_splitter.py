from PIL import Image
import os

# Open the image file
img = Image.open('tiles.png')  # replace with the path to your image file

# Get the size of the image
img_size = img.size

# Tile size
tile_size = 16

# Calculate the number of tiles in the x and y directions
num_tiles_x = img_size[0] // tile_size
num_tiles_y = img_size[1] // tile_size

# Create a directory to store the tile images
os.makedirs("tiles", exist_ok=True)

# Loop over the image
for i in range(num_tiles_y):
    for j in range(num_tiles_x):
        # Define the bounding box of the tile
        left = j * tile_size
        upper = i * tile_size
        right = (j + 1) * tile_size
        lower = (i + 1) * tile_size
        box = (left, upper, right, lower)

        # Crop the image to the bounding box
        tile = img.crop(box)

        # Save the tile to a PNG file
        tile.save(f"tiles/tile_{i}_{j}.png")
