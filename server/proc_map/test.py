import numpy as np
import matplotlib.pyplot as plt
from noise import snoise2

overworld = {
    'Forest': {'range': (0.15, 1.0), 'color': 'darkgreen', 'id': 0},
    'Grass': {'range': (-0.2, 0.15), 'color': 'green', 'id': 1},
    'Sand': {'range': (-0.25, -0.2), 'color': 'yellow', 'id': 2},
    'Water': {'range': (-0.35, -0.25), 'color': 'blue', 'id': 3},
    'DeepWater': {'range': (-1.0, -0.35), 'color': 'darkblue', 'id': 4}
}


# Color mapping from string to RGB
color_mapping = {
    'blue': [0, 0, 255],
    'darkblue': [0, 0, 100],
    'yellow': [255, 255, 0],
    'green': [0, 255, 0],
    'darkgreen': [0, 100, 0]
}

# Perlin noise settings
shape = (5000,5000)  # Lower resolution for faster testing
scale = 200.0
octaves = 6
persistence = 0.5
lacunarity = 2.0

# Generate Perlin noise map
world = np.zeros(shape)
for i in range(shape[0]):
    for j in range(shape[1]):
        world[i][j] = snoise2(i/scale, 
                              j/scale, 
                              octaves=octaves, 
                              persistence=persistence, 
                              lacunarity=lacunarity, 
                              repeatx=1024, 
                              repeaty=1024, 
                              base=0)

# Assign colors based on the terrain key
color_world = np.zeros((*world.shape, 3))  # We need an additional dimension for the RGB values
overworld_sorted = sorted(overworld.items(), key=lambda x: x[1]['range'][0])  # Sort terrains by range
for i in range(shape[0]):
    for j in range(shape[1]):
        for terrain, attributes in overworld_sorted:
            if attributes['range'][0] <= world[i][j] < attributes['range'][1]:
                color_world[i, j] = color_mapping[attributes['color']]  # Use the RGB values from the color_mapping
                break  # Break the loop as soon as a match is found

# Normalize the RGB values to the [0, 1] range
color_world = color_world / 255

# Save the map
plt.imsave('perlin.png', color_world)
