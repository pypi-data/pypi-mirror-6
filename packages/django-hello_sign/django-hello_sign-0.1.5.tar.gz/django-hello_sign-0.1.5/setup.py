# -*- coding: utf-8 -*-
import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-hello_sign",
    version = "0.1.5",
    author = "Ross Crawford-d'Heureuse",
    author_email = "ross@lawpal.com",
    description = ("Django app for integrating with HelloSign"),
    license = "MIT",
    keywords = "django hellosign app",
    url = "https://github.com/rosscdh/django-hello_sign",
    packages=['hello_sign'],
    install_requires = [
        'hellosign',
    ],
)
