#!/usr/bin/env python
from setuptools import setup

description = "Docs at http://github.com/boscoh/tohaml."

setup(
    name='tohaml',
    version='1.0.1',
    author='Bosco Ho',
    author_email='boscoh@gmail.com',
    url='http://github.com/boscoh/tohaml',
    description='converts HTML to HAML for the HamlPy compiler',
    long_description=description,
    license='BSD',
    install_requires=['beautifulsoup4'],
    scripts=['tohaml'],
    py_modules=['tohaml']
)