import flask
import flask.ext.pymongo
import unittest

class FlaskRequestTest(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask('test')
        self.context = self.app.test_request_context('/')
        self.context.push()

    def tearDown(self):
        self.context.pop()

class FlaskPyMongoTest(FlaskRequestTest):

    def setUp(self):
        super(FlaskPyMongoTest, self).setUp()

        self.dbname = self.__class__.__name__
        self.app.config['MONGO_DBNAME'] = self.dbname
        self.mongo = flask.ext.pymongo.PyMongo(self.app)
        self.mongo.cx.drop_database(self.dbname)

    def tearDown(self):
        self.mongo.cx.drop_database(self.dbname)

        super(FlaskPyMongoTest, self).tearDown()
