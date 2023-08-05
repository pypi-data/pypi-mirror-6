# -*- coding: utf-8 -*-
"""Installer for propertyshelf.fabfile.common."""

from setuptools import setup, find_packages

version = '0.1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(
    name='propertyshelf.fabfile.common',
    version=version,
    description='Commonly used fabric commands.',
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
    ],
    keywords='fabric python deployment',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://github.com/propertyshelf/propertyshelf.fabfile.common',
    download_url='http://pypi.python.org/pypi/propertyshelf.fabfile.common',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['propertyshelf', 'propertyshelf.fabfile'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'Fabric',
        'PyChef',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
