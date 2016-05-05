import os
import random
import string

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from pip.req import parse_requirements


def main():
    """
    Setup the project for a user.

    This involves creating a secret key, setting up groups and permissions.
    """

    template = os.path.join('lionel', 'example_settings.py')
    settings = os.path.join('lionel', 'settings.py')

    with open(template, 'r') as template_file, open(settings, 'w') as settings_file:
        settings_file.write(template_file.read().replace("SECRET_KEY = 'Enter your secret key here'",
                                                         "SECRET_KEY = '{}'".format(make_key())))

    package_setup()


def package_setup():

    reqs = [str(ir.req) for ir in parse_requirements('requirements.txt')]

    setup(name='lionel',
          version='0.1',
          description='Automated data wrangling with Django',
          author='Nick Sarbicki',
          author_email='nick.a.sarbicki@gmail.com',
          install_requires=reqs)


def make_key(pk=None):
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

if __name__ == '__main__':
    main()