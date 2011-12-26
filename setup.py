"""
Flask-PyMongo
-------------

PyMongo support for Flask applications.
"""

from setuptools import find_packages, setup

from flask_pymongo import __version__

setup(
    name='Flask-PyMongo',
    version=__version__,
    # url='',
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
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    tests_require=[
        'nose',
    ],
    test_suite='nose.collector',
)

