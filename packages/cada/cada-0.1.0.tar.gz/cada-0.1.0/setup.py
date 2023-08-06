#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys

from os.path import join
from setuptools import setup, find_packages

RE_REQUIREMENT = re.compile(r'^\s*-r\s*(?P<filename>.*)$')

PYPI_RST_FILTERS = (
    # Replace code-blocks
    (r'\.\.\s? code-block::\s*(\w|\+)+',  '::'),
    # Remove travis ci badge
    (r'.*travis-ci\.org/.*', ''),
    # Remove pypip.in badges
    (r'.*pypip\.in/.*', ''),
    (r'.*crate\.io/.*', ''),
    (r'.*coveralls\.io/.*', ''),
)


def rst(filename):
    '''
    Load rst file and sanitize it for PyPI.
    Remove unsupported github tags:
     - code-block directive
     - travis ci build badge
    '''
    content = open(filename).read()
    for regex, replacement in PYPI_RST_FILTERS:
        content = re.sub(regex, replacement, content)
    return content


def pip(filename):
    '''Parse pip requirement file and transform it to setuptools requirements'''
    requirements = []
    for line in open(join('requirements', filename)).readlines():
        match = RE_REQUIREMENT.match(line)
        if match:
            requirements.extend(pip(match.group('filename')))
        else:
            requirements.append(line)
    return requirements


long_description = '\n'.join((
    rst('README.rst'),
    ''
))

install_requires = pip('install.pip')

if sys.version_info[0:2] < (2, 7):
    install_requires += ['argparse']

setup(
    name='cada',
    version='0.1.0',
    description='Search and consult CADA advices',
    long_description=long_description,
    url='https://github.com/etalab/cada',
    author='Axel Haustant',
    author_email='axel@data.gouv.fr',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'sentry': pip('sentry.pip'),
    },
    entry_points={
        'console_scripts': [
            'cada = cada.commands:main',
        ]
    },
    license='AGPLv3+',
    keywords='cada',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    ],
)
