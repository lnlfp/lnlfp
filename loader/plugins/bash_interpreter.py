from ._interpreter import Interpreter

class BashInterpreter(Interpreter):
    """
    Basic interpreter for bash.
    """
    LANGUAGE = 'Bash'
    EXTENSION = '.sh'

    def run(self, file, *args, **kwargs):
        pass