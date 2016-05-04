import os
import random
import string

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Setup(BaseCommand):
    help = 'Set up the Lionel app'

    def add_arguments(self, parser):
        """
        Add the pk argument for this command. We want to be able to use --private-key to define a set SECRET_KEY for a
        user.
        """
        parser.add_argument('--private-key',
                            dest='pk',
                            default=False,
                            help='use the given private key')

    def handle(self, *args, **options):
        """
        Setup the project for a user.

        This involves creating a secret key, setting up groups and permissions.
        """
        template = os.path.join('lionel', 'example_settings.py')
        settings = os.path.join('lionel', 'settings.py')

        with open(template, 'r') as template_file, open(settings, 'w') as settings_file:
            settings_file.write(template_file.read().replace("SECRET_KEY = 'Enter your secret key here'",
                                                             "SECRET_KEY = '{}'".format(self.make_key(options['pk']))))

        pm = Group.objects.create(name='Project Manager')
        dev = Group.objects.create(name='Developer')
        worker = Group.objects.create(name='Worker')
        client = Group.objects.create(name='Client')

        add_feed = Permission.objects.create(name='Can Create Feeds', codename='can_add_feed')


    def make_key(self, pk):
        """
        Construct a SECRET_KEY if we don't already have one.

        :param pk: str, optional pk provided by the user.
        :return: str, SECRET_KEY to be used by this instance.
        """
        if pk:
            return pk
        else:
            chars = ''.join([string.ascii_letters, string.digits, string.punctuation]).replace('\'', '').replace('"', '').replace('\\', '')

            return ''.join([random.SystemRandom().choice(chars) for _ in range(50)])