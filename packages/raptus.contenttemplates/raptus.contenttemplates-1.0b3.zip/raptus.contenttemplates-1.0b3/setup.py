from setuptools import setup, find_packages
import os

version = '1.0b3'

setup(name='raptus.contenttemplates',
      version=version,
      description="Provides generic interfaces to create content templates using adapters",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Raptus AG',
      author_email='dev@raptus.com',
      url='https://github.com/Raptus/raptus.contenttemplates',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['raptus'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.z3cform',
          'zope.browsermenu',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
