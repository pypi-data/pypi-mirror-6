# -*- coding: utf-8 -*-
"""Installer for the collective.local.contentrules package."""

from setuptools import find_packages
from setuptools import setup


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
    name='collective.local.contentrules',
    version='1.0rc1',
    description="Adds string interpolators to get emails of the collaborators on a document.",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='contentrules,workspace',
    author='Thomas Desvenain',
    author_email='thomasdesvenain@ecreall.com',
    url='http://pypi.python.org/pypi/collective.local.contentrules',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.local'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.api',
    ],
    extras_require={
        'test': [
            'ecreall.helpers.testing',
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
