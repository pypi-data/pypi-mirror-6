#!/usr/bin/env python
from setuptools import setup

description = \
"""proteomics visualization generator

Docs at http://github.com/boscoh/peptagram.
"""

setup(
    name='peptagram',
    version='0.1a',
    author='Bosco Ho',
    author_email='boscoh@gmail.com',
    url='http://github.com/boscoh/peptagram',
    description='proteomics visualization generator',
    long_description=description,
    license='BSD',
    include_package_data = True,
    install_requires=[
        'uniprot',
        'pymzml',
    ],
    packages=['peptagram',],
    scripts=[],
)