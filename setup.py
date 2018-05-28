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

Source code is hosted in `GitHub <https://github.com/dcrosta/flask-pymongo>`_.
Contributions are welcome!
"""

from setuptools import find_packages, setup

setup(
    name="Flask-PyMongo",
    url="http://flask-pymongo.readthedocs.org/",
    download_url="https://github.com/dcrosta/flask-pymongo/tags",
    license="BSD",
    author="Dan Crosta",
    author_email="dcrosta@late.am",
    description="PyMongo support for Flask applications",
    long_description=__doc__,
    zip_safe=False,
    platforms="any",
    packages=find_packages(),
    install_requires=[
        "Flask>=0.11",
        "PyMongo>=3.0",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    setup_requires=["vcversioner"],
    vcversioner={"version_module_paths": ["flask_pymongo/_version.py"]},
)
