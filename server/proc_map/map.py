import cmd
import numpy as np
import noise
import os
import pickle
from scipy.spatial import Voronoi, voronoi_plot_2d, cKDTree
import tqdm
import cProfile
import pstats
import io
from collections import defaultdict
import time

from proc_map.poisson_points import poisson_disc_samples
from proc_map.resources import resources, overworld
# from poisson_points import poisson_disc_samples
# from resources import resources, overworld

profile_data = defaultdict(list)


def profile(func):
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        profile_data[func.__name__].append(s.getvalue())
        return result
    return wrapper


def write_profiles_to_file():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Use the current time to create a unique log file name
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f'logs/profile-{timestamp}.txt'

    with open(filename, 'w') as f:
        for func_name, profile_results in profile_data.items():
            for i, profile_result in enumerate(profile_results):
                f.write(f'\nProfiling: {func_name}, call {i+1}\n')
                f.write(profile_result)


class Map:
    def __init__(self, height=5000, width=5000, chunk_size=500, r=5, frequency=100, octaves=3, persistence=0.5, seed=69420):
        self.height = height
        self.width = width
        self.chunk_size = chunk_size
        self.r = r
        self.frequency = frequency
        self.octaves = octaves
        self.persistence = persistence
        self.seed = seed
        self.samples = None
        self.sample_resources = None
        np.random.seed(self.seed)
        import random
        random.seed(self.seed)

    @profile
    def generate_samples(self):
        self.samples = poisson_disc_samples(
            self.width, self.height, self.r, data_type='int', seed=self.seed)

    @profile
    def assign_resources_to_samples(self):
        sample_resources = []
        for _ in range(len(self.samples)):
            stage_resources = [np.random.choice(
                list(resources.keys()), p=self.normalize_weights(stage)) for stage in range(4)]
            sample_resources.append(stage_resources)
        self.sample_resources = sample_resources

    def normalize_weights(self, stage):
        weights = np.array([resources[resource]['stage'][stage]
                           for resource in resources])
        return weights / weights.sum()

    @profile
    def generate_map(self):
        if not self.samples:
            self.generate_samples()
        if not self.sample_resources:
            self.assign_resources_to_samples()
        # Generate a grid of coordinates
        y, x = np.mgrid[0:self.height, 0:self.width]

        # Compute Perlin noise values for the entire grid at once
        print("Generating Perlin noise map...")
        pnoise2 = np.vectorize(noise.pnoise2)
        world_map = pnoise2(x/self.frequency,
                            y/self.frequency,
                            octaves=self.octaves,
                            persistence=self.persistence,
                            repeatx=self.height,
                            repeaty=self.width,
                            base=self.seed)

        # Compute the nearest sample point for the entire grid at once
        print("Generating Voronoi map...")
        tree = cKDTree(self.samples)
        _, indices = tree.query(np.column_stack((y.ravel(), x.ravel())))
        indices = indices.reshape(self.height, self.width)

        # Compute the Voronoi diagram
        print("Assigning resource IDs...")
        # 5 layers: 4 stages + 1 Perlin
        voronoi_map = np.zeros((self.height, self.width, 5), dtype=int)
        for stage in tqdm.tqdm(range(4), desc="Stages"):  # Correct usage is tqdm.tqdm()
            voronoi_map[..., stage] = np.vectorize(
                lambda idx: resources[self.sample_resources[idx][stage]]['id'])(indices)

        # Compute the terrain type for the entire Perlin noise map at once
        print("Assigning terrain types...")
        terrain_types = np.array([(attributes['id'], attributes['range'][0], attributes['range'][1])
                                  for terrain_type, attributes in overworld.items()],
                                 dtype=[('id', 'i4'), ('start', 'f4'), ('end', 'f4')])
        terrain_types.sort(order='start')  # Sort by start of range
        indices = np.searchsorted(
            terrain_types['start'], world_map.ravel(), side='right') - 1
        voronoi_map[..., 4] = terrain_types['id'][indices].reshape(
            world_map.shape)

        print("Map generation complete.")
        self.generate_chunks(voronoi_map)
        return world_map, voronoi_map

    @profile
    def get_terrain_type(self, value):
        for terrain_type, attributes in overworld.items():
            if attributes['range'][0] <= value < attributes['range'][1]:
                return attributes['id']
        return 0  # Default to 'Water' if no other terrain type matches

    @profile
    def generate_chunks(self, voronoi_map):
        if not os.path.exists('chunks'):
            os.makedirs('chunks')

        for i in range(0, self.height, self.chunk_size):
            for j in range(0, self.width, self.chunk_size):
                chunk = voronoi_map[i:i+self.chunk_size,
                                    j:j+self.chunk_size, :].tolist()
                with open(f'chunks/chunk_{i}_{j}.pkl', 'wb') as f:
                    pickle.dump(chunk, f)

    @profile
    def get_region(self, x, y, r=50):
        min_x = max(0, x - r)
        min_y = max(0, y - r)
        max_x = min(self.width, x + r)
        max_y = min(self.height, y + r)
        region = [[[0]*5 for _ in range(max_x-min_x)]
                  for _ in range(max_y-min_y)]

        # Calculate chunk coordinates for all points in the region
        chunk_coords = [(i // self.chunk_size, j // self.chunk_size)
                        for i in range(min_x, max_x)
                        for j in range(min_y, max_y)]
        # Remove duplicates
        chunk_coords = list(set(chunk_coords))

        # Load all chunks into memory
        chunks = {}
        for chunk_x, chunk_y in chunk_coords:
            with open(f'proc_map/chunks/chunk_{chunk_x*self.chunk_size}_{chunk_y*self.chunk_size}.pkl', 'rb') as f:
                chunks[(chunk_x, chunk_y)] = pickle.load(f)

        # Extract points from chunks
        for i in range(min_x, max_x):
            for j in range(min_y, max_y):
                chunk_x, chunk_y = i // self.chunk_size, j // self.chunk_size
                chunk = chunks[(chunk_x, chunk_y)]
                region[j-min_y][i -
                                min_x] = chunk[(j % self.chunk_size)][(i % self.chunk_size)]
        return region


if __name__ == '__main__':
    map_object = Map()
