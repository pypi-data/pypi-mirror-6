

import os
from setuptools import setup, find_packages

version = '1.0'

test_require = [
    'plone.app.testing',
    'robotsuite',
    'robotframework-selenium2library',
    'decorator',
    'selenium',
]

setup(name='quintagroup.plonetabs',
      version=version,
      description="Quintagroup Plone Tabs",
      long_description=open("README.rst").read() + "\n" +
      open(os.path.join("docs", "HISTORY.rst")).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 3.2",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Security",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='quintagroup plonetabs',
      author='"Quintagroup": http://quintagroup.com/',
      author_email='support@quintagroup.com',
      url='http://quintagroup.com/'
          'services/plone-development/products/plone-tabs',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup'],
      include_package_data=True,
      zip_safe=False,
      tests_require=test_require,
      extras_require={'tests': test_require, },
      install_requires=[
          'setuptools',
          'plone.browserlayer'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
