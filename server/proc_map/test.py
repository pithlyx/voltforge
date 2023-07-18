
import cmd
from proc_map import Map


class Menu(cmd.Cmd):
    prompt = 'Menu> '

    def __init__(self, map_object):
        super().__init__()
        self.map = map_object

    def do_generate_samples(self, args):
        """Generate samples"""
        self.map.generate_samples()

    def do_assign_resources_to_samples(self, args):
        """Assign resources to samples"""
        self.map.assign_resources_to_samples()

    def do_generate_map(self, args):
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

    def do_write_profiles(self, args):
        """Write profiles to file"""
        write_profiles_to_file()

    def do_EOF(self, line):
        return True


if __name__ == '__main__':
    m = Map()
    Menu(m).cmdloop()
