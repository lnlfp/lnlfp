import subprocess

from ._interpreter import Interpreter


class PythonInterpreter(Interpreter):
    LANGUAGE = 'Python'
    EXTENSION = '.py'
    META = {}

    def run(self, file, *args, **kwargs):
        process = ['python', file.data.name] + args

        print(process)

        subprocess.Popen(process)