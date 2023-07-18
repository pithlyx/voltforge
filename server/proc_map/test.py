import numpy as np
import noise
import os
import pickle
from scipy.spatial import Voronoi, voronoi_plot_2d, cKDTree
from poisson_points import poisson_disc_samples
from resources import resources, overworld


class Map:
    def __init__(self, height, width, chunk_size, r, frequency, octaves, persistence, seed):
        self.height = height
        self.width = width
        self.chunk_size = chunk_size
        self.r = r
        self.frequency = frequency
        self.octaves = octaves
        self.persistence = persistence
        self.seed = seed
        np.random.seed(self.seed)
        import random
        random.seed(self.seed)
        self.samples = self.generate_samples()

    def generate_samples(self):
        return poisson_disc_samples(self.width, self.height, self.r, data_type='int', seed=None)

    def generate_map(self):
        world_map = np.zeros((self.height, self.width))
        voronoi_map = np.zeros((self.height, self.width), dtype=int)
        vor = Voronoi(self.samples)
        tree = cKDTree(self.samples)
        for i in range(self.height):
            for j in range(self.width):
                world_map[i][j] = noise.pnoise2(i/self.frequency,
                                                j/self.frequency,
                                                octaves=self.octaves,
                                                persistence=self.persistence,
                                                repeatx=self.height,
                                                repeaty=self.width,
                                                base=self.seed)
                _, idx = tree.query([i, j])
                voronoi_map[i][j] = idx
        return world_map, voronoi_map

    def get_terrain_type(self, value):
        for terrain_type, attributes in overworld.items():
            if attributes['range'][0] <= value < attributes['range'][1]:
                return attributes['id']
        return 0  # Default to 'Water' if no other terrain type matches

    def generate_chunks(self):
        world_map, voronoi_map = self.generate_map()
        world_map_id = np.zeros_like(world_map, dtype=int)
        for i in range(self.height):
            for j in range(self.width):
                world_map_id[i][j] = self.get_terrain_type(world_map[i][j])

        # Create the chunks directory if it doesn't already exist
        if not os.path.exists('chunks'):
            os.makedirs('chunks')

        # Save each chunk to a separate file
        for i in range(0, self.height, self.chunk_size):
            for j in range(0, self.width, self.chunk_size):
                chunk = [[world_map_id[y][x], voronoi_map[y][x]] for y in range(
                    i, i+self.chunk_size) for x in range(j, j+self.chunk_size)]
                with open(f'chunks/chunk_{i}_{j}.pkl', 'wb') as f:
                    pickle.dump(chunk, f)

    def get_region(self, x, y, r):
        min_x = max(0, x - r)
        min_y = max(0, y - r)
        max_x = min(self.width, x + r)
        max_y = min(self.height, y + r)
        region = [[0, 0] for _ in range((max_y-min_y)*(max_x-min_x))]

        for i in range(min_x, max_x):
            for j in range(min_y, max_y):
                chunk_x, chunk_y = i // self.chunk_size, j // self.chunk_size
                with open(f'chunks/chunk_{chunk_x*self.chunk_size}_{chunk_y*self.chunk_size}.pkl', 'rb') as f:
                    chunk = pickle.load(f)
                region[(j-min_y)*(max_x-min_x)+(i-min_x)] = chunk[(j %
                                                                   self.chunk_size)*self.chunk_size+(i % self.chunk_size)]

        return region


m = Map(height=1000, width=1000, chunk_size=100, r=5,
        frequency=100, octaves=4, persistence=0.5, seed=1)
m.generate_chunks()

# Test the get_region method
print(m.get_region(450, 450, 20))
