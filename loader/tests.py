from django.test import TestCase
from loader.models import File, Feed

class FileTestCase(TestCase):
    # TODO: Files need to have column methods tested.
    # TODO: Ensure every file has a feed and a user
    # TODO: Delimiter can't be more than one.

    pass

class FeedTestCase(TestCase):
    # TODO: Feeds cannot be accessed except by users in their users field.
    # TODO: They can only have unique names.
    # TODO: feed_directory_path returns an accurate path.
    pass
