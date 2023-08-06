from setuptools import setup, find_packages
import sys, os

def read(filename):
    return open(os.path.join(os.path.dirname(__file__),
                             filename)).read() + "\n\n"


version = '0.3'


setup(name='z3c.offlinepack',
      version=version,
      description="Pack ZODB databases without running Zope or ZEO",
      long_description=(
          read('README.rst') +
          read('CHANGES.rst')),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zodb pack',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='https://github.com/rpatterson/z3c.offlinepack',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'ZODB3', 'zope.dottedname'
      ],
      extras_require=dict(
          test=[
              'zc.buildout',
              'zc.recipe.egg',
              'zope.testing',
              ]),
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      offlinepack = z3c.offlinepack:main
      """,
      )
