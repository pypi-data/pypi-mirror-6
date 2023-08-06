# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


setup(name='rawgithub',
      version='0.1',
      description='rawgithub',
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
      ],
      keywords="web services",
      author=u'Rémy HUBSCHER',
      author_email='hubscher.remy@gmail.com',
      url='https://github.com/diecutter/rawgithub',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['cornice', 'waitress', 'requests'],
      entry_points={
          'paste.app_factory': [
              'main = rawgithub:main',
          ]
      },
      paster_plugins=['pyramid'])
