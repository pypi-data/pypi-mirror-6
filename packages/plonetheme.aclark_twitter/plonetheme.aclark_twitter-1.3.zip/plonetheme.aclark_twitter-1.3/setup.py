from setuptools import setup, find_packages
import os

version = '1.3'

setup(name='plonetheme.aclark_twitter',
      version=version,
      description="Complete silliness: make your Plone site look like Alex Clark's Twitter profile.",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='Alex Clark',
      author_email='aclark@aclark.net',
      url='https://github.com/collective/plonetheme.aclark_twitter/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonetheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      test_suite='plonetheme.aclark_twitter.tests.test_suite',
      )
