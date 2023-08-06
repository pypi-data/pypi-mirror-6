from tangled.abcs import ACommand


class Command(ACommand):

    @classmethod
    def configure(cls, parser):
        """Configure ``parser``.

        ``parser`` is an :class:`argparse.ArgumentParser`.

        """

    def run(self):
        """Implement the command's functionality."""
        print('`tangled auth` not yet implemented')
        print('Implement in ../tangled.auth/tangled/auth/command.py')
