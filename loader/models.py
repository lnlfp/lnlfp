import ast

from django.db import models
from django.contrib.auth.models import User


def feed_directory_path(instance, filename):
    """
    Function to return an upload path for new files.

    Takes a class instance and finds it's feedname, for the folder structure, and the upload date.

    Joining these with slashes and the filename itself gives the filepath.

    :param instance: File model instance, used to receive the feed name and the upload date.
    :param filename: str, name of the file being uploaded.
    :return: str, complete filepath and name for file to be uploaded.
    """
    return '{0}/{1}/{2}'.format(instance.feed.name,
                                instance.upload_date.strftime('%Y%m%d'),
                                filename)


class ListField(models.TextField):
    """
    Field which handles python lists.

    Subclasses the Textfield so we can hold a list as an arbitrarily lengthed string
    """
    __metaclass__ = models.SubfieldBase
    description = 'Holds a Python List'

    def __init__(self, *args, **kwargs):
        self.delimiter = kwargs.pop('delimiter')
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        When in Python, we want to use a python List, not a string.

        So convert the string to a list, unless it already is a list...

        :param value: str, the value of this field.
        :return: list, the list which the value represents
        """
        if not value:
            return []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        """
        Overwriting to_python necessitates reversing the process, so this converts a list back to a string.

        :param value: list, the field value as a list
        :return: str, the field value as a string.
        """
        if value:
            return str(value)
        else:
            return ''

    def value_to_string(self, obj):
        """
        Force serialisation to use get_prep_value.

        :param obj: object to be serialised
        :return: str, serialised object.
        """

        value = self.value_from_object(obj)

        return self.get_prep_value(value)


class File(models.Model):
    """
    Model to hold the file details.
    """

    #####################
    #  Relational Info  #
    #####################

    user = models.ForeignKey(User)
    feed = models.ForeignKey(Feed)

    #####################
    #  File Based Info  #
    #####################

    data = models.FileField(upload_to=feed_directory_path)
    file_name = models.CharField(null=False, max_length=100)
    upload_date = models.DateTimeField(auto_now_add=True)

    delimiter = models.CharField(null=True, max_length=1)
    columns = ListField(null=True)


class Feed(models.Model):
    """
    Model to hold the feed details.
    """

    #####################
    #  Relational Info  #
    #####################

    users = models.ManyToManyField(User)

    #####################
    #   Identity Info   #
    #####################

    name = models.CharField(max_length=50, unique=True)
