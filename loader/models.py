import ast

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
    return '{0}/{1}/{2}'.format(instance.feed.name,
                                instance.upload_date.strftime('%Y%m%d'),
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
    #   Identity Info   #
    #####################

    name = models.CharField(max_length=50, unique=True, null=False)


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

    delimiter = models.CharField(null=True, max_length=1, default=',')
    columns = models.TextField(null=True, blank=True)

    def get_columns(self):
        """
        Return file column headers as a list.

        :return: list, list of column header
        """
        if self.columns.split(self.delimiter):
            return self.columns.split(self.delimiter)
        else:
            return []

    def set_columns(self, lst):
        """
        Take a list of columns and set the columns property to a string representing this.

        :param lst: lst, a list representing the columns in this file.
        """

        self.columns = ','.join(lst)

    def clean(self, exclude=None):
        """
        We need to do some model validation to ensure the User given is acceptable.

        :param exclude:
        :return: None
        """
        if self.user not in self.feed.users.all():
            raise ValidationError('This User is not authorised to upload files to this feed!')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(File, self).save(*args, **kwargs)
