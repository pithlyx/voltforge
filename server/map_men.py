import cmd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from proc_map import Map, write_profiles_to_file

resources = {
    'Stone': {'stage': [0.7, 0.15, 0, 0.05], 'color': 'gray', 'id': 0},
    'Coal': {'stage': [0.3, 0.25, 0.15, 0.05], 'color': 'black', 'id': 1},
    'Copper': {'stage': [0, 0.3, 0.2, 0.1], 'color': 'red', 'id': 2},
    'Iron': {'stage': [0, 0.3, 0.2, 0.1], 'color': 'blue', 'id': 3},
    'Crude Oil': {'stage': [0, 0, 0.1, 0.1], 'color': 'brown', 'id': 4},
    'Silicon': {'stage': [0, 0, 0.12, 0.2], 'color': 'yellow', 'id': 5},
    'Limestone': {'stage': [0, 0, 0.18, 0.175], 'color': 'beige', 'id': 6},
    'Aluminum': {'stage': [0, 0, 0.05, 0.1], 'color': 'silver', 'id': 7},
    'Uranium': {'stage': [0, 0, 0, 0.025], 'color': 'green', 'id': 8},
    'Gold': {'stage': [0, 0, 0, 0.05], 'color': 'gold', 'id': 9},
    'Lithium': {'stage': [0, 0, 0, 0.05], 'color': 'purple', 'id': 10}
}
# Define the key for the Perlin noise map
overworld = {
    'DeepWater': {'range': (-1.0, -0.35), 'color': 'darkblue', 'id': 0},
    'Water': {'range': (-0.35, -0.25), 'color': 'blue', 'id': 1},
    'Sand': {'range': (-0.25, -0.2), 'color': 'yellow', 'id': 2},
    'Grass': {'range': (-0.2, 0.15), 'color': 'green', 'id': 3},
    'Forest': {'range': (0.15, 1.0), 'color': 'darkgreen', 'id': 4}
}


class Menu(cmd.Cmd):
    prompt = 'Menu >> '

    def __init__(self, map_object):
        super().__init__()
        self.map = map_object

    def do_generate_samples(self, args):
        """Generate samples"""
        self.map.generate_samples()

    def do_assign_resources_to_samples(self, args):
        """Assign resources to samples"""
        self.map.assign_resources_to_samples()

    def do_map(self, args):
        """Generate map"""
        self.map.generate_map()

    def do_generate_chunks(self, args):
        """Generate chunks"""
        self.map.generate_chunks()

    def do_quit(self, args):
        """Quit the program."""
        print("Quitting.")
        return True

    def do_get_region(self, args):
        """Get region. Arguments: x y r"""
        x, y = map(int, args.split())
        region = self.map.get_region(x, y)
        for row in region:
            for column in row:
                print(column, end=' ')
            print()

    def do_plot_region(self, arg):
        'Plot a region with the syntax: plot_region [x] [y] [r] [i]'
        x, y, r, i = map(int, arg.split())
        region = self.map.get_region(x, y, r, i)
        
        # Create a new figure and axes
        fig, ax = plt.subplots()

        # Choose the dictionary of resources or overworld based on the value of i
        keys = resources if i != 4 else overworld

        # Create a colormap and a normalization instance
        cmap = plt.cm.colors.ListedColormap([val['color'] for val in keys.values()])
        norm = plt.cm.colors.Normalize(vmin=0, vmax=len(keys) - 1)

        # Plot the region with the colormap
        ax.imshow(region, cmap=cmap, norm=norm)

        # Create a colorbar with the correct labels
        cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax, ticks=range(len(keys)))
        cbar.ax.set_yticklabels(list(keys.keys()))

        # Show the plot
        plt.show()

    def do_write_profiles(self, args):
        """Write profiles to file"""
        write_profiles_to_file()

    def do_EOF(self, line):
        return True


if __name__ == '__main__':
    m = Map(seed=14453)
    Menu(m).cmdloop()
