import subprocess

from ._interpreter import Interpreter


class PythonInterpreter(Interpreter):
    """
    Basic interpreter for Python.
    """
    LANGUAGE = 'Python'
    EXTENSION = '.py'

    def run(self, proc, *args):
        """
        Run a python script with the given args.

        :param proc: Procedure obj, the procedure we are running.
        :param args: list of arguments to pass to the command line.
        :return: str, stdoutput from the process.
        """
        process = ['python', proc.procedure.name] + args

        running = subprocess.Popen(process, stdout=subprocess.PIPE)

        while True:  # While this is running give out the output.
            outp = running.stdout.readline()
            if not outp:
                break
            yield outp
