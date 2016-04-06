class Interpreter:
    """
    Base interpreter class.

    All plugins need to inherit this class to be recognised.
    """
    LANGUAGE = None  # What language is this for?
    EXTENSION = None  # What is the standard file extension for programs of this language?
    META = {}  # What extra data is required to run this?

    def __init__(self):
        if not (self.LANGUAGE and self.EXTENSION):
            raise NotImplementedError('Class {} lacks the required properties.'.format(self.__class__.__name__))

    def run(self, file, *args, **kwargs):
        """
        Method used to run procedures.

        Raise an error here to make sure it gets overwritten.

        :param file: str, filepath to the procedure to run.
        :param args: list of arguments to attach to the procedure.
        """
        raise NotImplementedError('Class {} lacks a run method.'.format(self.__class__.__name__))
