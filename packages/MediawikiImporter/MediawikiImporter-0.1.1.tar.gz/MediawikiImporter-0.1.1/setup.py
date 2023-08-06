from setuptools import setup, find_packages

__version__ = '0.1.1'

setup(name='MediawikiImporter',
      version=__version__,
      description="Mediawiki Importer plugin for the Allura platform",
      long_description="",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Igor Bondarenko',
      author_email='jetmind2@gmail.com',
      url='http://sf.net/p/mediawikiimporter',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=['html2text'],
      entry_points="""
      # -*- Entry points: -*-
      [allura.importers]
      mediawiki = mediawikiimporter.importer:MediawikiImporter
      """,
      )
