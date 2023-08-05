#!/usr/bin/env python

from setuptools import setup

setup(
    name='Django-UserService',
    version='1.0',
    packages=[ 'userservice' ],
    install_requires=['Django'],
    license = "Apache 2.0",
    author = "Patrick Michaud",
    author_email = "pmichaud@uw.edu",
    description = "User abstraction and impersonation for Django",
    keywords = "django user",
    url = "https://github.com/vegitron/django-userservice"
)
