from setuptools import setup, find_packages
import os

version = '0.1'

tests_require = ['plone.app.testing']

setup(name='redomino.odttransforms',
      version=version,
      description="ODT templating transforms",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone',
      author='Davide Moro',
      author_email='davide.moro@redomino.com',
      url='http://redomino.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redomino'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'ooopy',
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
