from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='wmowonen.theme',
      version=version,
      description="Theme for WMO Wonen NH (2014)",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Four Digits',
      author_email='info@fourdigits.nl',
      url='http://www.fourdigits.nl',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wmowonen'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.theming',
          'plone.app.themingplugins',
          'collective.portletpage',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel", "fourdigits.skeleton"],
      )
