import numpy as np
from collections import deque
import random
# from test import profile, write_profiles_to_file


def euclidean_distance(p1, p2):
    """
    Compute the Euclidean distance between two points.
    """
    return np.sqrt(np.sum((p1 - p2) ** 2))


# @profile
def poisson_disc_samples(width, height, r, seed=None, k=5, data_type='float'):
    """
    Generate Poisson disc samples using a more efficient algorithm.
    """
    # If no seed is provided, generate a random seed
    seed = seed or random.randint(0, 1000000)
    random.seed(seed)  # Seed the random number generator
    print("Seed: {}".format(seed))

    tau = 2 * np.pi  # Constant for 2*pi
    cell_size = r / np.sqrt(2)  # The size of each cell in the grid

    # The number of cells along the width and height
    grid_width = int(np.ceil(width / cell_size))
    grid_height = int(np.ceil(height / cell_size))

    # Initialize the grid with None
    grid = [[None for _ in range(grid_height)] for _ in range(grid_width)]

    # Function to convert continuous coordinates to discrete grid coordinates
    def grid_coords(p):
        return int(p[0] // cell_size), int(p[1] // cell_size)

    # Generate a random initial point
    p = np.array([width * random.random(), height * random.random()])

    # The active list is implemented as a deque for efficient pops from the end
    active_list = deque([p])

    # The initial point is added to the grid
    gx, gy = grid_coords(p)
    grid[gx][gy] = p

    # The result list of points starts with the initial point
    points = [p]

    # While there are still points in the active list
    while active_list:
        # Randomly select a point from the active list
        idx = random.randint(0, len(active_list) - 1)
        # Swap the selected point with the one at the end of the active list
        active_list[idx], active_list[-1] = active_list[-1], active_list[idx]
        # Pop the selected point from the active list
        p = active_list.pop()

        # For each new candidate point around the selected point
        for _ in range(k):
            # Generate a random point within the annulus around the selected point
            alpha = tau * random.random()
            d = r * np.sqrt(3 * random.random() + 1)
            q = p + d * np.array([np.cos(alpha), np.sin(alpha)])

            # If the new point is outside the area, skip it
            if not (0 <= q[0] < width and 0 <= q[1] < height):
                continue

            # Get the grid cell of the new point
            gx, gy = grid_coords(q)

            # Check if the new point is too close to other points
            too_close = False

            # Iterate over the 3x3 grid cell neighborhood of the new point
            for x in range(max(gx - 1, 0), min(gx + 2, grid_width)):
                for y in range(max(gy - 1, 0), min(gy + 2, grid_height)):
                    # If the grid cell is not empty and the point in the cell is too close to the new point
                    if grid[x][y] is not None and euclidean_distance(q, grid[x][y]) < r:
                        too_close = True
                        break
                if too_close:
                    break
            if too_close:
                continue

            # If the new point is not too close to other points, add it to the active list and the grid
            active_list.append(q)
            grid[gx][gy] = q
            points.append(q)

    # If the desired data type is 'int', convert the points to integers
    if data_type == 'int':
        return np.array(points).astype(int)
    else:
        return points


if __name__ == "__main__":
    width, height = 2000, 2000  # Dimensions of the area
    r = 5  # Minimum distance between points
    # Generate Poisson disc samples
    samples = poisson_disc_samples(
        width, height, r, data_type='int', seed=None)
    write_profiles_to_file()
