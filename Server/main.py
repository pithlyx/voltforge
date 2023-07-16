# Importing necessary libraries and modules
import cmd
import sys
from proc_map import Map, plot_all_samples, plot_samples_in_radius

# Define a class MapCmd that extends from cmd.Cmd


class MapCmd(cmd.Cmd):
    def __init__(self):
        """Initializes the command line interface."""
        # Initialize the parent class
        super().__init__()
        # Set the welcome message
        self.intro = "Welcome to the Map command-line menu. Type 'help' for available commands."
        # Set the command prompt text
        self.prompt = "map>>> "
        # Create a map object
        self.map = Map(500, 500, 5, seed=None)

    def do_get_resource(self, args):
        """Command to get the resource at a point and stage.

        Args:
            args (str): The arguments string, expected to be "x y stage".
        """
        # Split the arguments string into a list
        args = args.split()
        # Check if the number of arguments is correct
        if len(args) != 3:
            print("Invalid number of arguments.")
            return
        try:
            # Convert the arguments to integers
            x, y, stage = map(int, args)
        except ValueError:
            # Handle the case where the arguments cannot be converted to integers
            print("Invalid arguments. Coordinates and stage must be integers.")
            return
        # Get the resource at the point and stage
        resource = self.map.get_resource_at_point([x, y], stage)
        # Print the resource
        print(f"The resource at ({x}, {y}) at stage {stage} is: {resource}")

    def do_plot_samples(self, args):
        """Command to plot the samples.

        Args:
            args (str): The arguments string, expected to be either empty
            or "x y radius stage".
        """
        # Split the arguments string into a list
        args = args.split()
        # Check if the arguments string is empty
        if len(args) == 0:
            # Plot all samples with the default stage 0
            plot_all_samples(self.map, 0)
        elif len(args) == 4:
            try:
                # Convert the arguments to integers
                x, y, radius, stage = map(int, args)
            except ValueError:
                # Handle the case where the arguments cannot be converted to integers
                print(
                    "Invalid arguments. Coordinates, radius and stage must be integers.")
                return
            # Plot the samples within a radius of a point
            plot_samples_in_radius(self.map, [x, y], radius, stage)
        else:
            # Handle the case where the number of arguments is incorrect
            print("Invalid number of arguments.")

    def do_exit(self, args):
        """Command to exit the command line interface.

        Args:
            args (str): The arguments string, expected to be empty.
        """
        print("Exiting...")
        sys.exit(0)

    def default(self, line):
        """Default method to handle invalid commands.

        Args:
            line (str): The command line.
        """
        print("Invalid command. Type 'help' for available commands.")


def main():
    """Main function to start the command line interface."""
    mapcmd = MapCmd()
    mapcmd.cmdloop()


if __name__ == "__main__":
    main()
