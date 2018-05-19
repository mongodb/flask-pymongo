Flask-PyMongo
=============

`MongoDB <http://www.mongodb.org/>`_ is an open source database that stores
flexible JSON-like "documents," which can have any number, name, or
hierarchy of fields within, instead of rows of data as in a relational
database. Python developers can think of MongoDB as a persistent, searchable
repository of Python dictionaries (and, in fact, this is how `PyMongo
<http://api.mongodb.org/python/current/>`_ represents MongoDB documents).

Flask-PyMongo bridges Flask and PyMongo, so that you can use Flask's normal
mechanisms to configure and connect to MongoDB.


Quickstart
----------

First, install Flask-PyMongo:

.. code-block:: bash

    $ pip install Flask-PyMongo

Flask-PyMongo depends, and will install for you, recent versions of Flask
(0.8 or later) and PyMongo (2.4 or later). Flask-PyMongo is compatible
with and tested on Python 2.6, 2.7, and 3.3.

Next, add a :class:`~flask_pymongo.PyMongo` to your code:

.. code-block:: python

    from flask import Flask
    from flask_pymongo import PyMongo

    app = Flask(__name__)
    mongo = PyMongo(app)

:class:`~flask_pymongo.PyMongo` connects to the MongoDB server running on
port 27017 on localhost, and assumes a default database name of ``app.name``
(i.e. whatever name you pass to :class:`~flask.Flask`). This database is
exposed as the :attr:`~flask_pymongo.PyMongo.db` attribute.

You can use :attr:`~flask_pymongo.PyMongo.db` directly in views:

.. code-block:: python

    @app.route('/')
    def home_page():
        online_users = mongo.db.users.find({'online': True})
        return render_template('index.html',
            online_users=online_users)


Helpers
-------

Flask-PyMongo provides helpers for some common tasks:

.. automethod:: flask_pymongo.wrappers.Collection.find_one_or_404

.. automethod:: flask_pymongo.PyMongo.send_file

.. automethod:: flask_pymongo.PyMongo.save_file

.. autoclass:: flask_pymongo.BSONObjectIdConverter

Configuration
-------------

:class:`~flask_pymongo.PyMongo` understands the following configuration
directives:

=====================================  =========================================
``MONGO_URI``                          A `MongoDB URI
                                       <http://www.mongodb.org/display/DOCS/Connections#Connections-StandardConnectionStringFormat>`_
                                       which is used in preference of the other
                                       configuration variables.
``MONGO_HOST``                         The host name or IP address of your
                                       MongoDB server. Default: "localhost".
``MONGO_PORT``                         The port number of your MongoDB server.
                                       Default: 27017.
``MONGO_AUTO_START_REQUEST``           Set to ``False`` to disable PyMongo 2.2's
                                       "auto start request" behavior (see
                                       :class:`~pymongo.mongo_client.MongoClient`).
                                       Default: ``True``.
``MONGO_MAX_POOL_SIZE``                (optional): The maximum number of idle
                                       connections maintained in the PyMongo
                                       connection pool. Default: PyMongo
                                       default.
``MONGO_SOCKET_TIMEOUT_MS``            (optional): (integer) How long (in
                                       milliseconds) a send or receive on a
                                       socket can take before timing out.
                                       Default: PyMongo default.
``MONGO_CONNECT_TIMEOUT_MS``           (optional): (integer) How long (in
                                       milliseconds) a connection can take to be
                                       opened before timing out.
                                       Default: PyMongo default.
``MONGO_SERVER_SELECTION_TIMEOUT_MS``  (optional) Controls how long (in
                                       milliseconds) the driver will wait to
                                       find an available, appropriate server to
                                       carry out a database operation; while it
                                       is waiting, multiple server monitoring
                                       operations may be carried out, each
                                       controlled by ``connectTimeoutMS``.
                                       Default: PyMongo default.
``MONGO_DBNAME``                       The database name to make available as
                                       the ``db`` attribute.
                                       Default: ``app.name``.
``MONGO_USERNAME``                     The user name for authentication.
                                       Default: ``None``
``MONGO_PASSWORD``                     The password for authentication.
                                       Default: ``None``
``MONGO_AUTH_SOURCE``                  The database to authenticate against.
                                       Default: ``None``
``MONGO_AUTH_MECHANISM``               The mechanism to authenticate with.
                                       Default: pymongo <3.x ``MONGODB-CR``
                                       else ``SCRAM-SHA-1``
``MONGO_REPLICA_SET``                  The name of a replica set to connect to;
                                       this must match the internal name of the
                                       replica set (as determined by the
                                       `isMaster
                                       <http://www.mongodb.org/display/DOCS/Replica+Set+Commands#ReplicaSetCommands-isMaster>`_
                                       command). Default: ``None``.
``MONGO_READ_PREFERENCE``              Determines how read queries are routed to
                                       the replica set members. Must be one of
                                       the constants defined on
                                       :class:`pymongo.read_preferences.ReadPreference`
                                       or the string names thereof.
``MONGO_DOCUMENT_CLASS``               This tells pymongo to return custom
                                       objects instead of dicts, for example
                                       ``bson.son.SON``. Default: ``dict``
``MONGO_CONNECT``                      (optional): If ``True`` (the default),
                                       let the MongoClient immediately begin
                                       connecting to MongoDB in the background.
                                       Otherwise connect on the first operation.
                                       This has to be set to ``False`` if
                                       multiprocessing is desired; see
                                       `Using PyMongo with Multiprocessing
                                       <https://api.mongodb.org/python/current/faq.html#multiprocessing>`_.
=====================================  =========================================

When :class:`~flask_pymongo.PyMongo` or
:meth:`~flask_pymongo.PyMongo.init_app` are invoked with only one argument
(the :class:`~flask.Flask` instance), a configuration value prefix of
``MONGO`` is assumed; this can be overridden with the `config_prefix`
argument.

This technique can be used to connect to multiple databases or database
servers:

.. code-block:: python

    app = Flask(__name__)

    # connect to MongoDB with the defaults
    mongo1 = PyMongo(app)

    # connect to another MongoDB database on the same host
    app.config['MONGO2_DBNAME'] = 'dbname_two'
    mongo2 = PyMongo(app, config_prefix='MONGO2')

    # connect to another MongoDB server altogether
    app.config['MONGO3_HOST'] = 'another.host.example.com'
    app.config['MONGO3_PORT'] = 27017
    app.config['MONGO3_DBNAME'] = 'dbname_three'
    mongo3 = PyMongo(app, config_prefix='MONGO3')

Some auto-configured settings that you should be aware of are:

``tz_aware``:
  Flask-PyMongo always uses timezone-aware :class:`~datetime.datetime`
  objects. That is, it sets the ``tz_aware`` parameter to ``True`` when
  creating a connection. The timezone of :class:`~datetime.datetime`
  objects returned from MongoDB will always be UTC.

``safe``:
  Flask-PyMongo sets "safe" mode by default, which causes
  :meth:`~pymongo.collection.Collection.save`,
  :meth:`~pymongo.collection.Collection.insert`,
  :meth:`~pymongo.collection.Collection.update`, and
  :meth:`~pymongo.collection.Collection.remove` to wait for acknowledgement
  from the server before returning. You may override this on a per-call
  basis by passing the keyword argument ``safe=False`` to any of the
  effected methods.


API
===

Constants
---------

.. autodata:: flask_pymongo.ASCENDING

.. autodata:: flask_pymongo.DESCENDING


Classes
-------

.. autoclass:: flask_pymongo.PyMongo
   :members:

.. autoclass:: flask_pymongo.wrappers.Collection
   :members:


Wrappers
--------

These classes exist solely in order to make expressions such as
``mongo.db.foo.bar`` evaluate to a
:class:`~flask_pymongo.wrappers.Collection` instance instead of
a :class:`pymongo.collection.Collection` instance. They are documented here
solely for completeness.

.. autoclass:: flask_pymongo.wrappers.MongoClient
   :members:

.. autoclass:: flask_pymongo.wrappers.MongoReplicaSetClient
   :members:

.. autoclass:: flask_pymongo.wrappers.Database
   :members:


History and Contributors
------------------------

Changes:

- 0.5.2: May 19, 2018

  - `#102 <https://github.com/dcrosta/flask-pymongo/pull/102>`_ Return 404,
    not 400, when given an invalid input to `BSONObjectIdConverter` (Abraham
    Toriz Cruz).

- 0.5.1: May 24, 2017

  - `#93 <https://github.com/dcrosta/flask-pymongo/pull/93>`_ Supply a
    default ``MONGO_AUTH_MECHANISM`` (Mark Unsworth).

- 0.5.0: May 21, 2017

    **This will be the last 0.x series release.** The next non-bugfix
    release will be Flask-PyMongo 2.0, which will introduce backwards
    breaking changes, and will be the foundation for improvements and
    changes going forward. Flask-PyMongo 2.0 will no longer support Python
    2.6, but will support Python 2.7 and Python 3.3+.

  - `#44 <https://github.com/dcrosta/flask-pymongo/issues/44>`_, `#51
    <https://github.com/dcrosta/flask-pymongo/pull/51>`_ Redirect ``/``
    to ``/HomePage`` in the wiki example (David Awad)
  - `#76 <https://github.com/dcrosta/flask-pymongo/pull/76>`_ Build on more
    modern Python versions (Robson Roberto Souza Peixoto)
  - `#79 <https://github.com/dcrosta/flask-pymongo/pull/79>`_, `#84
    <https://github.com/dcrosta/flask-pymongo/issues/84>`_, `#85
    <https://github.com/dcrosta/flask-pymongo/pull/85>`_ Don't use
    ``flask.ext`` import paths any more (ratson, juliascript)
  - `#40 <https://github.com/dcrosta/flask-pymongo/issues/40>`_, `#83
    <https://github.com/dcrosta/flask-pymongo/pull/83>`_, `#86
    <https://github.com/dcrosta/flask-pymongo/pull/86>`_ Fix options parsing
    from ``MONGO_URI`` (jobou)
  - `#72 <https://github.com/dcrosta/flask-pymongo/issues/72>`_, `#80
    <https://github.com/dcrosta/flask-pymongo/pull/80>`_ Support
    ``MONGO_SERVER_SELECTION_TIMEOUT_MS`` (Henrik Blidh)
  - `#34 <https://github.com/dcrosta/flask-pymongo/issues/34>`_, `#64
    <https://github.com/dcrosta/flask-pymongo/pull/64>`_, `#88
    <https://github.com/dcrosta/flask-pymongo/pull/88>`_ Support
    from ``MONGO_AUTH_SOURCE`` and ``MONGO_AUTH_MECHANISM`` (Craig Davis)
  - `#74 <https://github.com/dcrosta/flask-pymongo/issues/74>`_, `#77
    <https://github.com/dcrosta/flask-pymongo/issues/77>`_, `#78
    <https://github.com/dcrosta/flask-pymongo/pull/78>`_ Fixed ``maxPoolSize``
    in PyMongo 3.0+ (Henrik Blidh)
  - `#82 <https://github.com/dcrosta/flask-pymongo/issues/82>`_ Fix "another
    user is already authenticated" error message.
  - `#54 <https://github.com/dcrosta/flask-pymongo/issues/54>`_ Authenticate
    against "admin" database if no ``MONGO_DBNAME`` is provided.

- 0.4.1: January 25, 2016

  - Add the connect keyword:
    `#67 <https://github.com/dcrosta/flask-pymongo/pull/67>`_.

- 0.4.0: October 19, 2015

  - Flask-Pymongo is now compatible with pymongo 3.0+:
    `#63 <https://github.com/dcrosta/flask-pymongo/pull/63>`_.

- 0.3.1: April 9, 2015

  - Flask-PyMongo is now tested against Python 2.6, 2.7, 3.3, and 3.4.
  - Flask-PyMongo installation now no longer depends on `nose
    <https://pypi.python.org/pypi/nose/>`_.
  - `#58 <https://github.com/dcrosta/flask-pymongo/pull/58>`_ Update
    requirements for PyMongo 3.x (Emmanuel Valette).
  - `#43 <https://github.com/dcrosta/flask-pymongo/pull/43>`_ Ensure error
    is raised when URI database name is parsed as 'None' (Ben Jeffrey).
  - `#50 <https://github.com/dcrosta/flask-pymongo/pull/50>`_ Fix a bug in
    read preference handling (Kevin Funk).
  - `#46 <https://github.com/dcrosta/flask-pymongo/issues/46>`_ Cannot use
    multiple replicaset instances which run on different ports (Mark
    Unsworth).
  - `#30 <https://github.com/dcrosta/flask-pymongo/issues/30>`_
    ConfiguationError with MONGO_READ_PREFERENCE (Mark Unsworth).

- 0.3.0: July 4, 2013

  - This is a minor version bump which introduces backwards breaking
    changes! Please read these change notes carefully.
  - Removed read preference constants from Flask-PyMongo; to set a
    read preference, use the string name or import contants directly
    from :class:`pymongo.read_preferences.ReadPreference`.
  - `#22 (partial) <https://github.com/dcrosta/flask-pymongo/pull/22>`_
    Add support for ``MONGO_SOCKET_TIMEOUT_MS`` and
    ``MONGO_CONNECT_TIMEOUT_MS`` options (ultrabug).
  - `#27 (partial) <https://github.com/dcrosta/flask-pymongo/pull/27>`_
    Make Flask-PyMongo compatible with Python 3 (Vizzy).

- 0.2.1: December 22, 2012

  - `#19 <https://github.com/dcrosta/flask-pymongo/pull/19>`_ Added
    ``MONGO_DOCUMENT_CLASS`` config option (jeverling).

- 0.2.0: December 15, 2012

  - This is a minor version bump which may introduce backwards breaking
    changes! Please read these change notes carefully.
  - `#17 <https://github.com/dcrosta/flask-pymongo/pull/17>`_ Now using
    PyMongo 2.4's ``MongoClient`` and ``MongoReplicaSetClient`` objects
    instead of ``Connection`` and ``ReplicaSetConnection`` classes
    (tang0th).
  - `#17 <https://github.com/dcrosta/flask-pymongo/pull/17>`_ Now requiring
    at least PyMongo version 2.4 (tang0th).
  - `#17 <https://github.com/dcrosta/flask-pymongo/pull/17>`_ The wrapper
    class ``flask_pymongo.wrappers.Connection`` is renamed to
    ``flask_pymongo.wrappers.MongoClient`` (tang0th).
  - `#17 <https://github.com/dcrosta/flask-pymongo/pull/17>`_ The wrapper
    class ``flask_pymongo.wrappers.ReplicaSetConnection`` is renamed to
    ``flask_pymongo.wrappers.MongoReplicaSetClient`` (tang0th).
  - `#18 <https://github.com/dcrosta/flask-pymongo/issues/18>`_
    ``MONGO_AUTO_START_REQUEST`` now defaults to ``False`` when
    connecting using a URI.

- 0.1.4: December 15, 2012

  - `#15 <https://github.com/dcrosta/flask-pymongo/pull/15>`_ Added support
    for ``MONGO_MAX_POOL_SIZE`` (Fabrice Aneche)

- 0.1.3: September 22, 2012

  - Added support for configuration from MongoDB URI.

- 0.1.2: June 18, 2012

  - Updated wiki example application
  - `#14 <https://github.com/dcrosta/flask-pymongo/issues/14>`_ Added
    examples and docs to PyPI package.

- 0.1.1: May 26, 2012

  - Added support for PyMongo 2.2's "auto start request" feature, by way
    of the ``MONGO_AUTO_START_REQUEST`` configuration flag.
  - `#13 <https://github.com/dcrosta/flask-pymongo/pull/13>`_ Added
    BSONObjectIdConverter (Christoph Herr)
  - `#12 <https://github.com/dcrosta/flask-pymongo/pull/12>`_ Corrected
    documentation typo (Thor Adam)

- 0.1: December 21, 2011

  - Initial Release


Contributors:

- `jeverling <https://github.com/jeverling>`_
- `tang0th <https://github.com/tang0th>`_
- `Fabrice Aneche <https://github.com/akhenakh>`_
- `Thor Adam <https://github.com/thoradam>`_
- `Christoph Herr <https://github.com/jarus>`_
- `Mark Unsworth <https://github.com/markunsworth>`_
- `Kevin Funk <https://github.com/k-funk>`_
- `Ben Jeffrey <https://github.com/jeffbr13>`_
- `Emmanuel Valette <https://github.com/karec>`_
- `David Awad <https://github.com/DavidAwad>`_
- `Robson Roberto Souza Peixoto <https://github.com/robsonpeixoto>`_
- `juliascript <https://github.com/juliascript>`_
- `Henrik Blidh <https://github.com/hbldh>`_
- `jobou <https://github.com/jbouzekri>`_
- `Craig Davis <https://github.com/blade2005>`_
- `ratson <https://github.com/ratson>`_
- `Abraham Toriz Cruz <https://github.com/categulario>`_
