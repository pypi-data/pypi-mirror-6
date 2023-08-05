#!/usr/bin/env python
from setuptools import setup, find_packages
from billy import __version__

long_description = open('README.rst').read()

setup(name='billy',
      version=__version__,
      packages=find_packages(),
      package_data={'billy': ['schemas/*.json',
                              'schemas/api/*.json',
                              'schemas/relax/api.rnc'],
                    'billy.web.admin': ['templates/billy/*.html'],
                   },
      author="James Turk",
      author_email="jturk@sunlightfoundation.com",
      license="BSD",
      url="http://github.com/sunlightlabs/billy/",
      description='scraping, storing, and sharing legislative information',
      long_description=long_description,
      platforms=['any'],
      entry_points="""[console_scripts]
billy-update = billy.bin.update:main
billy-util = billy.bin.util:main
""",
      install_requires=[
          "Django>1.4,<1.5",
          "django-pjax",
          #"https://bitbucket.org/jespern/django-piston/get/tip.tar.gz",
          "boto",
          "icalendar",
          "lxml>=2.2",
          "name_tools>=0.1.2",
          "nose",
          "pymongo>=2.2",
          "scrapelib>=0.7.0",
          "unicodecsv!=0.9.3",
          "validictory",
          "pyelasticsearch",
      ]
)
