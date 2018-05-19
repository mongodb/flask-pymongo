"""
Flask-PyMongo
-------------

PyMongo support for Flask applications.

Installation
============

Flask-PyMongo is pip-installable:

    pip install Flask-PyMongo

You can install the latest development snapshot like so:

    pip install http://github.com/dcrosta/flask-pymongo/tarball/master#egg=Flask-PyMongo-dev

Upgrading
~~~~~~~~~

- Version 0.2.0 introduced a dependency on PyMongo version 2.4 or later, and
  introduced some potential backwards-breaking changes. Please review the
  `Changelog <http://flask-pymongo.readthedocs.org/en/latest/#history-and-contributors>`_
  carefully before upgrading.
- Version 0.3.0 removed the `ReadPreference
  <http://api.mongodb.org/python/current/api/pymongo/index.html#pymongo.read_preferences.ReadPreference>`_
  redefinitions in ``flask_pymongo``, in favor of using the constants directly
  from `PyMongo <http://api.mongodb.org/python/current/>`_. Please review the
  `Changelog <http://flask-pymongo.readthedocs.org/en/latest/#history-and-contributors>`_
  carefully before upgrading.

Development
===========

Source code is hosted in `GitHub <https://github.com/dcrosta/flask-pymongo>`_
(contributions are welcome!)
"""

from setuptools import find_packages, setup

setup(
    name='Flask-PyMongo',
    version='0.5.2',
    url='http://flask-pymongo.readthedocs.org/',
    download_url='https://github.com/dcrosta/flask-pymongo/tags',
    license='BSD',
    author='Dan Crosta',
    author_email='dcrosta@late.am',
    description='PyMongo support for Flask applications',
    long_description=__doc__,
    zip_safe=False,
    platforms='any',
    packages=find_packages(),
    install_requires=[line.strip() for line in open("requirements.txt")],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
