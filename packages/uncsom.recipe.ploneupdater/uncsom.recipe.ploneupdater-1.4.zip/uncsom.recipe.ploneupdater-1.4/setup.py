# -*- coding: utf-8 -*-
""" This module contains the tool of uncsom.recipe.ploneupdater """
import os
from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.4'

long_description = (
    read('README.md')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('src', 'uncsom', 'recipe', 'ploneupdater', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.rst')
    )
entry_point = 'uncsom.recipe.ploneupdater:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require = ['zope.testing', 'zc.buildout']

setup(name='uncsom.recipe.ploneupdater',
      version=version,
      description="A buildout recipe to update plone sites",
      long_description=long_description,
      classifiers=[
          'Framework :: Buildout',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: GNU General Public License (GPL)',],
      keywords='buildout recipe update plone',
      author='Ian Anderson',
      author_email='ianderso@med.unc.edu',
      url='https://github.com/ianderso/uncsom.recipe.ploneupdater',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['uncsom', 'uncsom.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools', 'zc.buildout'],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='uncsom.recipe.ploneupdater.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
