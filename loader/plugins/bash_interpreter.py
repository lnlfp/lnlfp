from ._interpreter import Interpreter

class BashInterpreter(Interpreter):
    LANGUAGE = 'Bash'
    EXTENSION = '.sh'

    def run(self, file, *args, **kwargs):
        pass