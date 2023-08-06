# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


_VERSION = '0.1'

def get_version():
    return _VERSION

setup(
    name='chamonix',
    license='GPLv3',
    description='Batteries for webpy application.',
    author='Chaobin Tang',
    author_email='cbtchn@gmail.com',
    url='https://github.com/chaobin/chamonix',
    version=get_version(),
    classifiers=[
        'Programming Language :: Python :: 2.6',
    ],
    packages = ['chamonix', 'chamonix.views'],
    install_requires=[
        'argparse',
        'python-gettext',
        'web.py',
        'icalendar',
        'pytz'
    ],
)