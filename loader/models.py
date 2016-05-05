import csv
import datetime
import json
import os

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
            return json.loads(self.columns)

        return []
        # what is this - why is columns not a list of columns?

    def set_columns(self, lst):
        """
        Take a list of columns and set the columns property to a string representing this.

        :param lst: lst, a list representing the columns in this file.
        """

        self.columns = json.dumps(lst)

    def get_first_lines(self, num=10):
        """
        Open the file and return the first few lines decided by num.

        :param num: int, the number of lines to be returned.
        :return: lst[str], the list of lines to be returned.
        """
        with open(self.data.name) as data_file:
            data = [next(data_file) for _ in range(num)]

        return data

    def get_table_info(self):
        """
        Do some initial sniffing to understand the format of a file.
        """
        dialect = csv.Sniffer().sniff(''.join(self.get_first_lines()))

        self.delimiter = dialect.delimiter

        self.terminator = dialect.lineterminator

        self.has_header = csv.Sniffer().has_header(''.join(self.get_first_lines()))
        
    def get_dataframe(self):
        '''
        Insert the file into a dataframe so we can anaylse it
        '''
        if self.has_header == True:
            skip = 1
        else:
            skip = 0
        self.df = pandas.read_csv( self.data.name
                                 , delimiter = self.delimiter
                                 , lineterminator = self.terminator
                                 , header = None
                                 , names = self.columns
                                 , skiprows = skip)
                                 
    def get_datatype_of_column(self, col):
        '''
        This tells us the sql friendly datatype of the column
        '''
        if self.df[col].dtype in ('float64', 'int64'):
            return 'number'
        if self.df[col].dtype == 'object':
            try:
                self.df[col] = pandas.to_datetime(self.df[col])
                return 'date'
            except ValueError:
                l_col_len = self.df[col].str.len().max()
                return 'varchar2(' + str(l_col_len) + ')'
        
    def get_column_info(self):
        '''
        Get some information on the columns so we can determine datatypes and 
        a primary key for loading the table 
        '''
        column_types = [self.get_datatype_of_column(e) for e in self.columns]
        no_of_uniques = [self.df[e].nunique() for e in self.columns]
        number_of_nulls = list(self.df.isnull().sum())
        # column_pos = list(range(0, len(columns) +1))
        column_info_dict = dict(zip(columns, zip(column_pos, column_types, no_of_uniques, number_of_nulls)))
        self.column_info = zip(self.columns, column_types, no_of_uniques, number_of_nulls)        

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
                     'upload_date':file.upload_date.isoformat(),
                     'columns': file.columns,
                     'user': file.user.username,
                     'user_email': file.user.email}

        json_args = json.dumps(file_args, separators=(',', ':'))

        self.LANGUAGE_INTERPRETER[self.language].run(self, json_args, *args)

    def __str__(self):
        """
        Create a human readable string for procedures.

        :return: str, the script name and it's description
        """

        return self.procedure.name + '\n\nDescription:\n' + self.comments