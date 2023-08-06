#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

PYPI_RST_FILTERS = (
    # Replace code-blocks
    (r'\.\.\s? code-block::\s*(\w|\+)+', '::'),
    # Replace image
    (r'\.\.\s? image::.*', ''),
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


def required(filename):
    with open(filename) as f:
        packages = f.read().splitlines()

    return packages


setup(
    name="serialkiller-plugins",
    version="0.0.2",
    description="Plugins for serialkiller project",
    long_description=rst('README.rst') + rst('CHANGELOG.txt'),
    author="Bruno Adelé",
    author_email="Bruno Adelé <bruno@adele.im>",
    url="https://github.com/badele/serialkiller-plugins",
    license="GPL",
    install_requires=required('requirements/base.txt'),
    setup_requires=[],
    tests_require=[
        'pep8',
        'coveralls'
    ],
    test_suite='tests',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=[],
    classifiers=[
        'Programming Language :: Python',
    ],
)
