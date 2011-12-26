# Flask-PyMongo

PyMongo support for Flask applications

## Quickstart

    from flask import Flask
    from flask.ext.pymongo import PyMongo

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
