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

With Flask-PyMongo installed, you can add a :class:`~flask_pymongo.PyMongo`
to your code:

.. code-block:: python

    from flask import Flask
    from flask.ext.pymongo import PyMongo

    app = Flask(__name__)
    mongo = PyMongo(app)

The :class:`~flask_pymongo.PyMongo` object has two attributes of note:
:attr:`~flask_pymongo.PyMongo.cx`, the
:class:`~pymongo.connection.Connection` object, and
:attr:`~flask_pymongo.PyMongo.db`, the
:class:`~pymongo.database.Database` object corresponding to the MongoDB
database with the same name as your flask app. In the example above, this
would be whichever name ``__name__`` resolves to (i.e. the name of the
Python module in which it is defined).

You can then use the :attr:`~flask_pymongo.PyMongo.db` attribute directly in
views:

.. code-block:: python

    @app.route('/')
    def home_page():
        online_users = mongo.db.users.find({'online': True})
        return render_template('index.html',
            online_users=online_users)


Helpers
-------

Flask-PyMongo provides helpers for some common tasks:

.. automethod:: flask_pymongo.Collection.find_one_or_404

.. automethod:: flask_pymongo.PyMongo.send_file

.. automethod:: flask_pymongo.PyMongo.save_file

Configuration
-------------

Flask-PyMongo adds three new configuration directives to Flask:

================ ==========================================================
``MONGO_HOST``   The host name or IP address of your MongoDB server.
                 Default: `localhost`.
``MONGO_PORT``   The port number of your MongoDB server. Default: `27017`.
``MONGO_DBNAME`` The database name to make available as the ``db``
                 attribute. Default: ``app.name`` (the first argument to
                 :class:`~flask.Flask`).
================ ==========================================================

When :class:`~flask_pymongo.PyMongo` is invoked with only one argument (the
:class:`~flask.Flask` instance), a configuration value prefix of ``MONGO``
is assumed; this can be overridden with the `config_prefix` argument to
:meth:`~flask_pymongo.PyMongo.__init__`.

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


API
===

.. autoclass:: flask_pymongo.PyMongo
   :members:

