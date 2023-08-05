#!/usr/bin/env python

from setuptools import setup, find_packages
import os

version = '0.1.1'

setup(name='hmc.theme',
      version=version,
      description="The Diazo based theme for hmc.csuohio.edu.",
      long_description=open("README.rst").read() + "\n" +
                       open("HISTORY.rst").read(),
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='theme plone',
      author='Jason K. Moore',
      author_email='j.k.moore19@csuohio.edu',
      url='http://github.com/csu-hmc/hmc.theme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['hmc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.theming',
          'plonetheme.diazo_sunburst',
      ],
      extras_require={
          'test': ['plone.app.testing']
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
