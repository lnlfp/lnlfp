import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from loader.models import File, Feed

class FileTestCase(TestCase):
    def setUp(self):
        """
        Need to set up a few base users and a feed.

        The feed should only allow access for one of the two users so we can test auth rules.

        :return: None
        """
        self.good_user = User.objects.create_user('good', 'good@example.com', 'password')
        self.bad_user = User.objects.create_user('bad', 'bad@example.com', 'password')

        self.usable_feed = Feed.objects.create(name='test_feed')
        self.usable_feed.users.add(self.good_user)

        self.usable_feed.save()

        self.sample_columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    def test_needs_feed(self):
        """
        Ensure that a File requires a feed

        :return: None
        """
        with self.assertRaises(Feed.DoesNotExist):
            File.objects.create(user=self.good_user, file_name='test.csv')

    def test_needs_user(self):
        """
        Ensure that a File requires a user.

        :return: None
        """
        with self.assertRaises(User.DoesNotExist):
            File.objects.create(feed=self.usable_feed, file_name='test.csv')

    def test_needs_file_name(self):
        """
        Ensure a File requires a file_name.

        :return: None
        """
        with self.assertRaises(ValidationError):
            File.objects.create(feed=self.usable_feed, user=self.good_user)

    def test_authorised_user(self):
        """
        Ensure that a File can only take an authorised user for it's feed.

        :return: None
        """
        f_good = File(feed=self.usable_feed, user=self.good_user, file_name='test.csv')
        f_good.clean()
        with self.assertRaises(ValidationError):
            f_bad = File(feed=self.usable_feed, user=self.bad_user)
            f_bad.clean()

    def test_created_date(self):
        """
        Ensure that the upload_date is the day a File is created.

        :return: None
        """
        file = File.objects.create(feed=self.usable_feed, user=self.good_user, file_name='test.csv')
        self.assertEqual(file.upload_date.date(), datetime.date.today())

    def test_file_path(self):
        pass

    def test_columns(self):
        """
        Ensure that get columns always returns a list.

        Ensure that set_columns takes a list. columns should then have this list joined by the delimiter.
        Ensure get_columns returns the same string split into a list.

        :return:
        """
        file = File(user=self.good_user, feed=self.usable_feed, file_name='test.csv')

        self.assertEqual(file.get_columns(), [])

        file.set_columns(self.sample_columns)

        self.assertEqual(file.columns, ','.join(self.sample_columns))

        self.assertEqual(file.get_columns(), self.sample_columns)

    def test_delimiter(self):
        """
        Ensure that columns returns with the expected delimiter given to the file. And that this does not affect get or
        set columns.

        :return: None
        """
        file = File(user=self.good_user, feed=self.usable_feed, file_name='test.csv', delimiter='|')

        file.set_columns(self.sample_columns)

        self.assertEqual(file.columns, '|'.join(self.sample_columns))

        self.assertEqual(file.get_columns(), self.sample_columns)


class FeedTestCase(TestCase):
    # TODO: feed_directory_path returns an accurate path.
    def setUp(self):
        """
        Set up testing with a feed to test.

        :return: None
        """
        self.feed = Feed.objects.create(name='Test Name')

    def test_str(self):
        """
        Over simple test to make sure __str__ works correctly.

        :return: None
        """
        self.assertEqual(str(self.feed.name), 'Test Name')

    def test_uniqueness(self):
        """
        Ensure an error is raised if we make multiple feeds with the same name.

        :return: None
        """
        pass


class ColumnTestCase(TestCase):
    pass