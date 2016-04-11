import csv
import datetime
import json
import os
import pandas

from django.contrib.auth.models import User
from django.db import models, connection

from loader import plugins


def feed_directory_path(instance, filename):
    """
    Function to return an upload path for new files.

    Takes a class instance and finds it's feedname, for the folder structure, and the upload date.

    Joining these with slashes and the filename itself gives the filepath.

    :param instance: File model instance, used to receive the feed name and the upload date.
    :param filename: str, name of the file being uploaded.
    :return: str, complete filepath and name for file to be uploaded.
    """
    return os.path.join('uploads',
                        instance.feed.name,
                        datetime.datetime.now().strftime('%Y-%m-%d'),
                        filename)


def proc_directory_path(instance, filename):
    """
    Function to return an upload path for new files.

    Takes a class instance and finds it's feedname, for the folder structure, and the upload date.

    Joining these with slashes and the filename itself gives the filepath.

    :param instance: File model instance, used to receive the feed name and the upload date.
    :param filename: str, name of the file being uploaded.
    :return: str, complete filepath and name for file to be uploaded.
    """
    return os.path.join('procedures',
                        instance.language,
                        filename)


class Feed(models.Model):
    """
    Model to hold the feed details.
    """

    #####################
    #  Relational Info  #
    #####################

    users = models.ManyToManyField(User)

    #####################
    # Identifying Info  #
    #####################

    name = models.CharField(max_length=50, unique=True, null=False)

    def __str__(self):
        """
        Return name of feed for when it is represented.

        :return: str, name of feed
        """
        return self.name


class Column(models.Model):
    """
    We need to recognise where some columns have special significance.

    These may have to be identified for some process later on.
    """

    ####################
    # Identifying Info #
    ####################

    name = models.CharField(max_length=50, unique=True)
    col_type = models.CharField(max_length=30)
    comment = models.CharField(max_length=400, null=True)

    def __str__(self):
        """
        Return name of column for when it is represented.

        :return: str, name of column.
        """

        return self.name


class File(models.Model):
    """
    Model to hold the file details.
    """

    #####################
    #  Relational Info  #
    #####################

    user = models.ForeignKey(User)
    feed = models.ForeignKey(Feed)
    special_columns = models.ManyToManyField(Column)

    #####################
    #  File Based Info  #
    #####################

    has_header = models.BooleanField(default=True)

    data = models.FileField(upload_to=feed_directory_path, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    delimiter = models.CharField(null=True, max_length=1, default=',')
    terminator = models.CharField(null=True, max_length=4, default='\n')

    #####################
    #   Database Info   #
    #####################

    table = models.CharField(max_length=30, blank=True)

    columns = models.TextField(null=True, blank=True)

    def get_columns(self):
        """
        Return file column headers as a list.

        :return: list, list of column header
        """
        if self.columns:
            if self.columns.split(self.delimiter):
                return self.columns.split(self.delimiter)

        return []

    def set_columns(self, lst):
        """
        Take a list of columns and set the columns property to a string representing this.

        :param lst: lst, a list representing the columns in this file.
        """

        self.columns = self.delimiter.join(lst)

    def get_first_lines(self):
        with open(self.data.name) as data_file:
            data = [next(data_file) for _ in range(10)]

        return data

    def get_table_info(self):
        dialect = csv.Sniffer().sniff(''.join(self.get_first_lines()))

        self.delimiter = dialect.delimiter

        self.terminator = dialect.lineterminator

        self.has_header = csv.Sniffer().has_header(''.join(self.get_first_lines()))

    def open_cursor(self):
        """
        Return a cursor to the database

        :return: cursor object.
        """
        return connection.cursor()

    def __str__(self):
        """
        concatenate upload date and file name to provide rough storage location.

        :return: str, identifying string for this file.
        """
        return os.path.split(self.data.name)[-1]


class Procedure(models.Model):
    """
    Model to hold a runnable procedure for a file.
    """

    #####################
    #   Language Info   #
    #####################

    LANGUAGE_CHOICES = ((plugin.LANGUAGE, plugin.LANGUAGE) for plugin in plugins.PLUGINS)

    LANGUAGE_EXTENSIONS = {plugin.LANGUAGE: plugin.EXTENSION for plugin in plugins.PLUGINS}

    LANGUAGE_INTERPRETER = {plugin.LANGUAGE: plugin for plugin in plugins.PLUGINS}

    language = models.CharField(max_length=10,
                                choices=LANGUAGE_CHOICES)

    #####################
    #  Procedure Info   #
    #####################

    name = models.CharField(max_length=20, blank=False)

    comments = models.CharField(max_length=400, blank=False)

    procedure = models.FileField(upload_to=proc_directory_path)

    user = models.ForeignKey(User)  # Store whoever designed the procedure so we can track ownership.

    def run(self, file, *args):
        """
        Call up a subprocess to run our procedures.

        :param file: File obj, the file we are running this on.
        :param args: tuple, list of arguments to add onto the call
        """

        file_args = {'table': file.table,
                     'upload_date':file.upload_date,
                     'columns': file.columns,
                     'user': file.user.name,
                     'user_email': file.user.email}

        json_args = json.dumps(file_args)

        self.LANGUAGE_INTERPRETER[self.language].run(self.procedure.file, json_args, *args)

    def __str__(self):
        """
        :return: str, the script name and it's description
        """

        return self.procedure.name + '\n\nDescription:\n' + self.comments
