#!/usr/bin/env python

"""
Setup script for python-veracity.
"""

import os
from setuptools import setup

from veracity import __project__, TRACKING, POLLER, BUILDER

setup(
    name=__project__,
    version='0.0.11',

    description="Python wrapper for Veracity's command-line interface.",
    url='http://pypi.python.org/pypi/python-veracity',
    author='Jace Browning',
    author_email='jacebrowning@gmail.com',

    packages=['veracity', 'veracity.test'],
    package_data={'veracity': ['files/*'], 'veracity.test': ['files/*']},

    entry_points={'console_scripts': [TRACKING + ' = veracity.tracking:main',
                                      POLLER + ' = veracity.poller:main',
                                      BUILDER + ' = veracity.builder:main']},
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    license='LGPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',  # pylint: disable=C0301
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Version Control',
    ],

    install_requires=["pbs >= 0.110" if os.name == 'nt' else "sh >= 1.0.8",
                      "virtualenv >= 1.9.1"],
)
