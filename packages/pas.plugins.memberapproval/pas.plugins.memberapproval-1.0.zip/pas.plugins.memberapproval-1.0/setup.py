# -*- coding: utf-8 -*-
"""
This module contains the tool of pas.plugins.memberapproval
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.txt')
    + '\n' +
    read('docs', 'INSTALL.txt')
    + '\n' +
    read('docs', 'CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs', 'CHANGES.txt')
    + '\n')

setup(name='pas.plugins.memberapproval',
      version=version,
      description="Member approval PAS plugin",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone pas',
      author='Radim Novotny',
      author_email='novotny.radim@gmail.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      namespace_packages=['pas', 'pas.plugins'],
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      extras_require = {
          'test': [
              'plone.app.testing',
              'interlude',
              'zope.globalrequest',
          ]
      }, 
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""
      # -*- entry_points -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
