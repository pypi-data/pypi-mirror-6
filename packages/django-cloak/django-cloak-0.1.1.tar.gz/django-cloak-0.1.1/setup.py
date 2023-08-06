#!/usr/bin/env python
from shutil import rmtree
from setuptools import setup

setup(
    name="django-cloak",
    version=__import__('cloak').__version__,
    url='https://github.com/PSU-OIT-ARC/django-cloak',
    author='Matt Johnson',
    author_email='mdj2@pdx.edu',
    description="App for Django to cloak as a user, or generate a login link",
    packages=['cloak','cloak.management', 'cloak.management.commands'],
    zip_safe=False,
    install_requires=[
        'django',
    ],
    classifiers=[
        'Framework :: Django',
    ],
)
