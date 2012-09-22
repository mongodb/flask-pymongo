import flask
import flask.ext.pymongo
import util
import warnings

import pymongo

class FlaskPyMongoConfigTest(util.FlaskRequestTest):

    def setUp(self):
        self.app = flask.Flask('test')
        self.context = self.app.test_request_context('/')
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def test_default_config_prefix(self):
        self.app.config['MONGO_DBNAME'] = 'flask_pymongo_test_db'
        self.app.config['MONGO_HOST'] = 'localhost'
        self.app.config['MONGO_PORT'] = 27017

        mongo = flask.ext.pymongo.PyMongo(self.app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        assert mongo.cx.host == 'localhost'
        assert mongo.cx.port == 27017

    def test_custom_config_prefix(self):
        self.app.config['CUSTOM_DBNAME'] = 'flask_pymongo_test_db'
        self.app.config['CUSTOM_HOST'] = 'localhost'
        self.app.config['CUSTOM_PORT'] = 27017

        mongo = flask.ext.pymongo.PyMongo(self.app, 'CUSTOM')
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        assert mongo.cx.host == 'localhost'
        assert mongo.cx.port == 27017

    def test_converts_str_to_int(self):
        self.app.config['MONGO_DBNAME'] = 'flask_pymongo_test_db'
        self.app.config['MONGO_HOST'] = 'localhost'
        self.app.config['MONGO_PORT'] = '27017'

        mongo = flask.ext.pymongo.PyMongo(self.app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        assert mongo.cx.host == 'localhost'
        assert mongo.cx.port == 27017

    def test_rejects_invalid_string(self):
        self.app.config['MONGO_PORT'] = '27017x'

        self.assertRaises(TypeError, flask.ext.pymongo.PyMongo, self.app)

    def test_sets_after_request_in_21(self):
        # fake PyMongo version 2.1; 2.2 uses auto_start_request
        original_tuple = pymongo.version_tuple
        original_version = pymongo.version

        pymongo.version_tuple = (2, 1)
        pymongo.version = '2.1'

        flask.ext.pymongo.PyMongo(self.app)

        pymongo.version_tuple = original_tuple
        pymongo.version = original_version

        print pymongo
        assert len(self.app.after_request_funcs.get(None, [])) == 1, 'did not set after_request handler'

    def test_does_not_set_after_request_in_22(self):
        # fake PyMongo version 2.2, which uses auto_start_request
        original_tuple = pymongo.version_tuple
        original_version = pymongo.version

        pymongo.version_tuple = (2, 2)
        pymongo.version = '2.2'

        flask.ext.pymongo.PyMongo(self.app)

        pymongo.version_tuple = original_tuple
        pymongo.version = original_version

        assert None not in self.app.after_request_funcs, 'set unneeded after_request handler'

    def test_multiple_pymongos(self):
        for prefix in ('ONE', 'TWO'):
            self.app.config['%s_DBNAME' % prefix] = prefix

        for prefix in ('ONE', 'TWO'):
            flask.ext.pymongo.PyMongo(self.app, config_prefix=prefix)

        # this test passes if it raises no exceptions

    def test_config_with_uri(self):
        self.app.config['MONGO_URI'] = 'mongodb://localhost:27017/flask_pymongo_test_db'

        with warnings.catch_warnings():
            # URI connections without a username and password
            # work, but warn that auth should be supplied
            warnings.simplefilter('ignore')
            mongo = flask.ext.pymongo.PyMongo(self.app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        assert mongo.cx.host == 'localhost'
        assert mongo.cx.port == 27017

    def test_config_with_uri_no_port(self):
        self.app.config['MONGO_URI'] = 'mongodb://localhost/flask_pymongo_test_db'

        with warnings.catch_warnings():
            # URI connections without a username and password
            # work, but warn that auth should be supplied
            warnings.simplefilter('ignore')
            mongo = flask.ext.pymongo.PyMongo(self.app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        assert mongo.cx.host == 'localhost'
        assert mongo.cx.port == 27017
