#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'wikify',
    version = '1.3',
    author = 'anatoly techtonik',
    author_email = 'techtonik@gmail.com',
    license = 'Public Domain',
    description = 'wikify your texts! micro-framework for text wikification',
    long_description = open('README.md', 'rb').read(),

    py_modules=['wikify']
)
