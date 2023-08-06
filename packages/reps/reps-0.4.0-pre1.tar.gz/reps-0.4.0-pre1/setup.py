import os

from setuptools import find_packages
from setuptools import setup

import reps


setup(
    name='reps',
    version=reps.__version__,
    description='Multiple repository management tool',
    author='Martin Matusiak',
    author_email='numerodix@gmail.com',
    url='https://github.com/numerodix/re',

    packages=find_packages('.'),
    package_dir = {'': '.'},

    install_requires=[
        'ansicolor',
        'ordereddict',
    ],

    # don't install as zipped egg
    zip_safe=False,

    scripts=[
        'bin/re',
    ],

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
