# Flask-PyMongo 2.0 Coming Soon

Keeping up with PyMongo and MongoDB developments has been a continual
struggle for me as maintainer of Flask-PyMongo, as attested to by the long
list of bugs filed. I have let down those who use this project, and I
apologize for that.

In order to make the maintenance load acceptable, I have decided to release
version 2.0 which will remove all of the "split out" configuration
functionality. In 2.0, Flask-PyMongo will only read a MongoDB connection URI
from Flask config. For cases where some configuration cannot be passed via
URI, it will also accept keyword arguments, which will be passed directly to
PyMongo.

I anticipate that this will require changes from many users of
Flask-PyMongo, and I apologize for the disruption. I believe that this
direction will enable me to keep up with compatibility requests, reduce the
number of custom forked versions, and provide a more compact and stable
platform for future development.

If you have not yet done so, please pin your version of Flask-PyMongo to the
current version (e.g. `flask-pymongo<2.0` in a `requirements.txt` file).

Please use https://github.com/dcrosta/flask-pymongo/issues/110 if you have
any questions or concerns with this decision.


# Flask-PyMongo

PyMongo support for Flask applications

## Quickstart

    from flask import Flask
    from flask_pymongo import PyMongo

    app = Flask(__name__)
    mongo = PyMongo(app)

    @app.route('/')
    def home_page():
        online_users = mongo.db.users.find({'online': True})
        return render_template('index.html',
            online_users=online_users)

## More Info

* [Flask-PyMongo Documentation](http://flask-pymongo.readthedocs.org/)
* [PyMongo Documentation](http://api.mongodb.org/python/current/)
* [Flask Documentation](http://flask.pocoo.org/docs/)
