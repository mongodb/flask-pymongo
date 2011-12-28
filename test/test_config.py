import flask
import flask.ext.pymongo
import util

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

    def test_rejects_invalid_strint(self):
        self.app.config['MONGO_PORT'] = '27017x'

        self.assertRaises(TypeError, flask.ext.pymongo.PyMongo, self.app)

    def test_sets_after_request(self):
        flask.ext.pymongo.PyMongo(self.app)
        assert len(self.app.after_request_funcs[None]) == 1, 'did not set after_request handler'

    def test_multiple_pymongos(self):
        for prefix in ('ONE', 'TWO'):
            self.app.config['%s_DBNAME' % prefix] = prefix

        for prefix in ('ONE', 'TWO'):
            flask.ext.pymongo.PyMongo(self.app, config_prefix=prefix)

        # this test passes if it raises no exceptions

