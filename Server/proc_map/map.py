# Import necessary libraries
from scipy.spatial import cKDTree
from proc_map.poisson_points import poisson_disc_samples
import numpy as np
from proc_map.resources import resources

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

    def get_resource_at_point(self, point, stage):
        """Get the resource at a given point and stage.
        Args:
            point (list): The point to get the resource at.
            stage (int): The stage to get the resource at.
        Returns:
            str: The resource at the given point and stage.
        """
        # Query the kd-tree to find the nearest sample point to the given point
        _, index = self.kd_tree.query(point)
        # Return the resource assigned to the nearest sample point at the given stage
        return self.maps[stage][index]
