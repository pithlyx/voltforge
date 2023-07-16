# Import necessary libraries
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
import numpy as np
from proc_map.resources import resources

# Function to plot all samples on the map


def plot_all_samples(map_obj, stage=0, plot_name='test'):
    """Plot all samples on the map.

    Args:
        map_obj (Map): The map object to plot.
        stage (int, optional): The stage of the samples. Defaults to 0.
        plot_name (str, optional): The name of the plot. Defaults to 'test'.
    """
    # Get the resources assigned to the samples for the given stage
    voronoi_resources = map_obj.maps[stage]

    # Create a new figure and a set of subplots
    fig, ax = plt.subplots()

    # Get the colors of the resources
    colors = [resources[resource]['color'] for resource in voronoi_resources]

    # Plot the samples with their respective colors
    ax.scatter(map_obj.samples[:, 0], map_obj.samples[:, 1],
               c=colors, marker='o', label='All Points')

    # Set the limits of the x and y axes
    ax.set_xlim([0, map_obj.samples[:, 0].max()])
    ax.set_ylim([0, map_obj.samples[:, 1].max()])

    # Add a legend to the plot
    ax.legend()

    # Set the aspect ratio of the plot to be equal
    ax.set_aspect('equal')

    # Save the plot as a PNG file
    plt.savefig(f"./img/points-{plot_name}.png")


# Function to plot samples within a certain radius of a point
def plot_samples_in_radius(map_obj, point, radius, stage=0, plot_name='test'):
    """Plot samples in a given radius of a point.

    Args:
        samples (list): The samples to plot.
        point (list): The point to plot samples around.
        radius (float): The radius to plot samples in.
        stage (int, optional): The stage of the samples. Defaults to 0.
        plot_name (str, optional): The name of the plot. Defaults to 'test'.
    """
    # Get the resources assigned to the samples for the given stage
    voronoi_resources = map_obj.maps[stage]

    # Find the indices of samples within the given radius of the point
    nearby_points_indices = map_obj.kd_tree.query_ball_point(point, radius)

    # Get the samples within the given radius of the point
    points_in_radius = map_obj.samples[nearby_points_indices]

    # Create a Voronoi diagram from the samples within the given radius of the point
    vor = Voronoi(points_in_radius)

    # Create a new figure and a set of subplots
    fig, ax = plt.subplots()

    # Get the colors and labels of the resources assigned to the samples within the given radius of the point
    colors = [resources[voronoi_resources[i]]['color']
              for i in nearby_points_indices]
    labels = [voronoi_resources[i] for i in nearby_points_indices]

    # Plot the Voronoi diagram with the respective colors and labels
    plot_voronoi(vor, colors, labels, point, radius)


# Function to plot a Voronoi diagram
def plot_voronoi(vor, colors, labels, point, radius):
    """Plot a Voronoi diagram.

    Args:
        vor (scipy.spatial.Voronoi): The Voronoi diagram to plot.
        colors (list): The colors of the cells in the diagram.
        labels (list): The labels of the cells in the diagram.
        point (list): The point to plot the diagram around.
        radius (float): The radius to plot the diagram in.
    """
    # Create a new figure and a set of subplots
    fig, ax = plt.subplots()

    # Plot the points in the Voronoi diagram
    ax.plot(vor.points[:, 0], vor.points[:, 1], 'k.')

    # For each region in the Voronoi diagram
    for i, region in enumerate(vor.point_region):
        # If the region is bounded
        if not -1 in vor.regions[region]:
            # Get the vertices of the region
            polygon = [vor.vertices[i] for i in vor.regions[region]]
            # If all vertices are within the given radius of the point
            if all((point[0] - radius <= p[0] <= point[0] + radius) and (point[1] - radius <= p[1] <= point[1] + radius) for p in polygon):
                # Fill the region with its respective color
                ax.fill(*zip(*polygon), colors[i])
                # Compute the centroid of the region
                centroid = np.mean(polygon, axis=0)
                # Add the label of the region at its centroid
                ax.text(*centroid, labels[i], ha='center')

    # Set the limits of the x and y axes
    ax.set_xlim([max(point[0] - radius, 0),
                min(point[0] + radius, vor.points[:, 0].max())])
    ax.set_ylim([max(point[1] - radius, 0),
                min(point[1] + radius, vor.points[:, 1].max())])

    # Set the aspect ratio of the plot to be equal
    ax.set_aspect('equal')

    # Save the plot as a PNG file
    plt.savefig(f"./img/voronoi-{point[0]}-{point[1]}-{radius}.png")
