# Import necessary libraries
from scipy.spatial import cKDTree
from proc_map.poisson_points import poisson_disc_samples
import numpy as np
from proc_map.resources import resources
from noise import snoise2
# Define a class called "Map"


class Map:
    def __init__(self, width, height, r, seed=None):
        """Initialize a map with width, height, and minimum distance between points.
        Args:
            width (int): The width of the map.
            height (int): The height of the map.
            r (float): The minimum distance between points.
            seed (int, optional): The seed for the random number generator. Defaults to None.
        """
        # Define the attributes of the class
        self.width = width  # Width of the map
        self.height = height  # Height of the map
        self.r = r  # Minimum distance between points
        self.resources = resources  # Get the resources dictionary
        np.random.seed(seed)  # Set the seed for the random number generator
        # Generate Poisson disk samples and convert them to numpy array
        self.samples = np.array(self.create_samples())
        # Construct a kd-tree from the samples for fast nearest-neighbor search
        self.kd_tree = cKDTree(self.samples)
        # Assign resources to the samples for 4 stages
        self.maps = [self.assign_resources(stage) for stage in range(4)]
        self.maps = np.array(self.maps)

    def create_samples(self):
        """Generate samples using Poisson disc sampling.
        Returns:
            list: The generated samples.
        """
        # Use the Poisson disc sampling function from the proc_map.poisson_points module to generate samples
        return poisson_disc_samples(self.width, self.height, self.r, data_type='int', seed=None)

    def assign_resources(self, stage):
        """Assign resources to the sample points.
        Args:
            stage (int): The stage of resource assignment.
        Returns:
            list: The resources assigned to the sample points.
        """
        # Get the names of the resources
        resource_names = list(self.resources.keys())
        # Get the probabilities of the resources for the given stage
        resource_probs = [self.resources[resource]['stage'][stage]
                          for resource in resource_names]
        # Randomly assign resources to the sample points according to the probabilities
        return np.random.choice(resource_names, size=len(self.samples), p=resource_probs)

    def generate_perlin_noise(self, point, radius, frequency, octaves, persistence):
        """Generate a Perlin noise map around a given point.

        Args:
            point (list): The center point of the Perlin noise map.
            radius (float): The radius of the Perlin noise map.
            frequency (float): The frequency of the Perlin noise.
            octaves (int): The number of octaves in the Perlin noise.
            persistence (float): The persistence value of the Perlin noise.

        Returns:
            np.ndarray: The generated Perlin noise map.
        """
        # Calculate the dimensions of the noise map
        map_width = int(radius * 2)
        map_height = int(radius * 2)

        # Calculate the starting coordinates for generating the noise
        start_x = int(point[0] - radius)
        start_y = int(point[1] - radius)

        # Generate the Perlin noise map
        noise_map = np.zeros((map_width, map_height))
        for y in range(map_height):
            for x in range(map_width):
                nx = start_x + x
                ny = start_y + y
                noise_map[x, y] = snoise2(
                    nx * frequency, ny * frequency, octaves=octaves, persistence=persistence)

        return noise_map
