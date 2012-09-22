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

Development
===========

Source code is hosted in `GitHub <https://github.com/dcrosta/flask-pymongo>`_
(contributions are welcome!)

"""

from setuptools import find_packages, setup

setup(
    name='Flask-PyMongo',
    version='0.1.3',
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
    install_requires=[
        'Flask >= 0.8',
        'pymongo >= 2.1',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    setup_requires=['nose'],
    tests_require=['nose', 'coverage'],
    test_suite='nose.collector',
)

