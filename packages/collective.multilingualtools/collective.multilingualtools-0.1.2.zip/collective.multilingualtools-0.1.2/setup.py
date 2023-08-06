# -*- coding: utf-8 -*-
"""
This module contains the collective.multilingualtools package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1.2'

long_description = (
    read('README.rst')
    + '\n' +
    read('docs/CHANGES.rst')
    + '\n' +
    read('docs/CONTRIBUTORS.rst')
    + '\n')

install_requires = [
        'setuptools',
        'plone.app.multilingual[dexterity, archetypes]',
    ]


setup(name='collective.multilingualtools',
    version=version,
    description="A set of tools that simplify handling multilingual "\
    "content in Plone using plone.app.multilingual.",
    long_description=long_description,
    classifiers=[
    "Framework :: Plone",
    "Framework :: Plone :: 4.0",
    "Framework :: Plone :: 4.1",
    "Framework :: Plone :: 4.2",
    "Framework :: Plone :: 4.3",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "License :: OSI Approved :: European Union Public Licence "\
        "1.1 (EUPL 1.1)",
    ],
    keywords='translation multilingual internationalization',
    author='Syslab.com GmbH',
    author_email='thomas@syslab.com',
    url='https://github.com/collective/collective.multilingualtools',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': [
            'plone.app.testing>=4.2.2',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
