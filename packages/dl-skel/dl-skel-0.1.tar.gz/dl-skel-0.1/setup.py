# -*- coding: utf-8 -*-
""" dlskel setup.py script """

# dl-skel
from dlskel import __version__

# system
#try:
from setuptools import setup
#except ImportError:
#    from distutils.core import setup
from os.path import join, dirname


setup(
    name='dl-skel',
    version=__version__,
    description='DoubleLeft skeleton generator',
    author='vitorfaleiros',
    author_email='barrabin.fc@gmail.com',
    packages=['dlskel'],
    scripts=['bin/dl-skel.py'],
    url='http://doubleleft.github.com/dl-skel',
    long_description=open('README.md').read(),
    install_requires=['kaptan','blessings','sh','jinja2','requests'],
    #test_suite='dlskel.test',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
      ],
)
