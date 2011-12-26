import flask
import flask.ext.pymongo
import unittest

class FlaskPyMongoConfigTest(unittest.TestCase):

    def test_default_config_prefix(self):
        app = flask.Flask('test')
        app.config['MONGO_DBNAME'] = 'flask_pymongo_test_db'
        app.config['MONGO_HOST'] = 'localhost'
        app.config['MONGO_PORT'] = 27017

        mongo = flask.ext.pymongo.PyMongo(app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        assert mongo.cx.host == 'localhost'
        assert mongo.cx.port == 27017

    def test_custom_config_prefix(self):
        app = flask.Flask('test')
        app.config['CUSTOM_DBNAME'] = 'flask_pymongo_test_db'
        app.config['CUSTOM_HOST'] = 'localhost'
        app.config['CUSTOM_PORT'] = 27017

        mongo = flask.ext.pymongo.PyMongo(app, 'CUSTOM')
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        assert mongo.cx.host == 'localhost'
        assert mongo.cx.port == 27017

    def test_converts_str_to_int(self):
        app = flask.Flask('test')
        app.config['MONGO_DBNAME'] = 'flask_pymongo_test_db'
        app.config['MONGO_HOST'] = 'localhost'
        app.config['MONGO_PORT'] = '27017'

        mongo = flask.ext.pymongo.PyMongo(app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        assert mongo.cx.host == 'localhost'
        assert mongo.cx.port == 27017

    def test_rejects_invalid_strint(self):
        app = flask.Flask('test')
        app.config['MONGO_PORT'] = '27017x'

        self.assertRaises(TypeError, flask.ext.pymongo.PyMongo, app)

    def test_sets_after_request(self):
        app = flask.Flask('test')
        app.config['MONGO_DBNAME'] = 'flask_pymongo_test_db'

        mongo = flask.ext.pymongo.PyMongo(app)
        assert mongo._after_request in app.after_request_funcs[None], 'did not set after_request handler'

