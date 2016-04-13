import subprocess

from ._interpreter import Interpreter


class OracleInterpreter(Interpreter):
    """
    Basic interpreter for Oracle.
    """
    LANGUAGE = 'oracle'
    EXTENSION = '.sql'

    @staticmethod
    def run(proc, *args):
        """
        Run a python script with the given args.

        :param proc: Procedure obj, the procedure we are running.
        :param args: list of arguments to pass to the command line.
        :return: str, stdoutput from the process.
        """

        process = ['sqlplus', 'inbound/*@s1', '@' + proc.procedure.name] + list(args)

        running = subprocess.Popen(process, stdout=subprocess.PIPE)

        output = []

        while True:  # While this is running give out the output.
            outp = running.stdout.readline()
            if not outp:
                break
            output.append(outp)

        return output