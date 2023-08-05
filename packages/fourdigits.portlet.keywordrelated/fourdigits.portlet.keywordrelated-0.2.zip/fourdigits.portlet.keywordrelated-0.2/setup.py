from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='fourdigits.portlet.keywordrelated',
      version=version,
      description="A portlet showing related items, "
                  "based on the current contexts tags.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("CHANGES.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Four Digits',
      author_email='info@fourdigits.nl',
      url='https://github.com/collective/fourdigits.portlet.keywordrelated',
      license='gpl',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['fourdigits', 'fourdigits.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': [
              'plone.app.testing',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
