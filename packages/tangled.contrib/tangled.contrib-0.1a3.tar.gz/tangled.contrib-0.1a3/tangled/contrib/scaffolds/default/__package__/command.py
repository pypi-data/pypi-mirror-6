from tangled.abcs import ACommand


class Command(ACommand):

    @classmethod
    def configure(cls, parser):
        """Configure ``parser``.

        ``parser`` is an :class:`argparse.ArgumentParser`.

        """

    def run(self):
        """Implement the command's functionality."""
        print('`tangled ${package}` not yet implemented')
        print('Implement in ${package_dir}/command.py')
