# Import necessary libraries
import numpy as np
from collections import deque
import random


def minkowski_distance(p1, p2, p=2):
    """
    Compute the Minkowski distance between two points.

    Args:
        p1 (np.array): The first point.
        p2 (np.array): The second point.
        p (int, optional): The order of the Minkowski distance. Defaults to 2.

    Returns:
        float: The Minkowski distance between the two points.
    """
    return np.sum(np.abs(p1 - p2) ** p) ** (1 / p)


def poisson_disc_samples(width, height, r, seed=None, k=5, p=2, data_type='float'):
    """
    Generate Poisson disc samples.

    Args:
        width (int): The width of the area to generate samples in.
        height (int): The height of the area to generate samples in.
        r (float): The minimum distance between samples.
        seed (int, optional): The seed for the random number generator. Defaults to None.
        k (int, optional): The number of new points to generate around each point. Defaults to 5.
        p (int, optional): The order of the Minkowski distance used in the generation of samples. Defaults to 2.
        data_type (str, optional): The data type of the returned samples. Defaults to 'float'.

    Returns:
        list or np.array: The generated samples. The data type of the samples depends on the `data_type` argument.
    """
    # If no seed is provided, generate a random seed
    seed = seed if seed else random.randint(0, 1000000)
    random.seed(seed)  # Seed the random number generator
    print("Seed: {}".format(seed))

    tau = 2 * np.pi  # Constant for 2*pi
    cell_size = r / np.sqrt(2)  # The size of each cell in the grid
    # The number of cells along the width
    grid_width = int(np.ceil(width / cell_size))
    # The number of cells along the height
    grid_height = int(np.ceil(height / cell_size))
    # Initialize the grid with None
    grid = [[None for _ in range(grid_height)] for _ in range(grid_width)]

    # Function to convert continuous coordinates to discrete grid coordinates
    def grid_coords(p):
        return int(p[0] // cell_size), int(p[1] // cell_size)

    # Function to check if a point can be placed at a position without violating the minimum distance constraint
    def fits(p):
        gx, gy = grid_coords(p)  # Get the grid coordinates of the point
        # Check cells within a 2-cell distance
        for x in range(max(gx - 2, 0), min(gx + 3, grid_width)):
            for y in range(max(gy - 2, 0), min(gy + 3, grid_height)):
                # If the cell is occupied and the distance to the point in the cell is less than r, return False
                if grid[x][y] is not None and minkowski_distance(p, grid[x][y]) <= r:
                    return False
        return True  # If no violations are found, return True

    # Generate a random initial point
    p = np.array([width * random.random(), height * random.random()])
    queue = deque([p])  # Initialize a deque with the initial point
    gx, gy = grid_coords(p)  # Get the grid coordinates of the initial point
    grid[gx][gy] = p  # Place the initial point on the grid

    # Continue generating points until the queue is empty
    while queue:
        # Randomly select an index in the queue
        qi = random.randint(0, len(queue) - 1)
        qx, qy = queue[qi]  # Get the point at the selected index
        # Rotate the queue so that the selected point is at the beginning
        queue.rotate(-qi)
        queue.popleft()  # Remove the selected point from the queue
        # Generate k new points around the selected point
        for _ in range(k):
            alpha = tau * random.random()  # Random angle
            # Random distance within the annulus of inner radius r and outer radius 2r
            d = r * np.sqrt(3 * random.random() + 1)
            px, py = qx + d * np.cos(alpha), qy + d * \
                np.sin(alpha)  # New point
            # If the new point is outside the area, skip it
            if not (0 <= px < width and 0 <= py < height):
                continue
            p = np.array([px, py])  # Create a numpy array for the new point
            # If the new point doesn't fit into the grid, skip it
            if not fits(p):
                continue
            queue.append(p)  # Add the new point to the end of the queue
            # Get the grid coordinates of the new point
            gx, gy = grid_coords(p)
            grid[gx][gy] = p  # Place the new point on the grid

    # Gather all points in the grid
    points = [p for row in grid for p in row if p is not None]
    # If the desired data type is 'int', convert the points to integers
    if data_type == 'int':
        return np.array(points).astype(int)
    else:
        return points


if __name__ == "__main__":
    width, height = 1000, 1000  # Dimensions of the area
    r = 10  # Minimum distance between points
    # Generate Poisson disc samples
    samples = poisson_disc_samples(
        width, height, r, data_type='int', seed=None)

    # These two lines refer to functions that are not defined in this script. They would have to be defined elsewhere in order to use them.
    kd_tree = build_kd_tree(samples)  # Build a kd-tree from the samples

    query_pt = [50, 50]  # A point of interest
    radius = 15  # Radius around the point of interest
    # Query points within the radius around the point of interest
    nearby_points_indices = query_points(kd_tree, query_pt, radius)
    # Get the actual points from their indices
    nearby_points = [samples[i] for i in nearby_points_indices]

    # Print the points within the radius around the point of interest
    print("Points within radius {} of {}: {}".format(
        radius, query_pt, nearby_points))
