import datetime
import os
import subprocess

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


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
                        datetime.datetime.now().strftime('%Y/%m/%d'),
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
                        instance.language
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
    feed =  models.ForeignKey(Feed)
    special_columns = models.ManyToManyField(Column)

    #####################
    #  File Based Info  #
    #####################

    has_header = models.BooleanField(default=True)

    data = models.FileField(upload_to=feed_directory_path, blank=True)
    file_name = models.CharField(null=False, max_length=100)
    upload_date = models.DateTimeField(auto_now_add=True)

    delimiter = models.CharField(null=True, max_length=1, default=',')
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

    def clean(self, exclude=None):
        """
        We need to do some model validation to ensure the User given is acceptable.
        """
        if self.user not in self.feed.users.all():
            raise ValidationError('This User is not authorised to upload files to this feed!')

    def save(self, *args, **kwargs):
        """
        This is called before committing.

        We need to use it to call the clean method which will validate relevant fields.

        :param args: arbitrary list of arguments for super method.
        :param kwargs: arbitrary dictionary or arguments for super method
        :return: result of super function
        """
        self.full_clean()
        return super(File, self).save(*args, **kwargs)

    def __str__(self):
        """
        concatenate upload date and file name to provide rough storage location.

        :return: str, identifying string for this file.
        """
        return self.upload_date.strftime('%Y%m%d') + '/' + self.file_name


class Procedure(models.Model):
    """
    Model to hold a runnable procedure for a file.
    """

    #####################
    #   Language Info   #
    #####################

    BASH = 'Bash'
    PYTHON = 'Python'
    ORACLE = 'Oracle'
    POSTGRES = 'Postgres'
    MYSQL = 'MySQL'

    LANGUAGE_CHOICES = ((BASH, 'Bash'),
                        (PYTHON, 'Python'),
                        (ORACLE, 'Oracle'),
                        (POSTGRES, 'Postgres'),
                        (MYSQL, 'MySQL')
                        )

    LANGUAGE_EXTENSIONS = {BASH: '.sh',
                           PYTHON: '.py',
                           ORACLE: '.sql',
                           POSTGRES: '.sql',
                           MYSQL: '.sql'
                           }

    LANGUAGE_CALL = {BASH: [],
                     PYTHON: ['python'],
                     ORACLE: ['sqlplus'],
                     POSTGRES: ['psql'],
                     MYSQL: ['mysql']
                     }

    language = models.CharField(max_length=10,
                                choices=LANGUAGE_CHOICES,
                                default=BASH)

    #####################
    #  Procedure Info   #
    #####################

    comments = models.CharField(max_length=400, blank=False)

    procedure = models.FileField(upload_to=proc_directory_path)

    def run(self, *args):
        """
        Call up a subprocess to run our procedures.
        :param args: tuple, list of arguments to add onto the call
        """
        subprocess.call(self.LANGUAGE_CALL[self.language] + list(args))

    def clean(self, exclude=None):
        """
        We need to do some model validation to ensure the procedure has the right extension and language
        """
        if not self.procedure.name.endswith(self.LANGUAGE_EXTENSIONS[self.language]):
            raise ValidationError('The file extension does not match the language picked!')

    def save(self, *args, **kwargs):
        """
        This is called before committing.

        We need to use it to call the clean method which will validate relevant fields.

        :param args: arbitrary list of arguments for super method.
        :param kwargs: arbitrary dictionary or arguments for super method
        :return: result of super function
        """
        self.full_clean()
        return super(File, self).save(*args, **kwargs)

    def __str__(self):
        """
        :return: str, the script name and it's description
        """

        return self.procedure.name + '\n\nDescription:\n' + self.comments