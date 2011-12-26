import flask
import flask.ext.pymongo
import unittest

class FlaskPyMongoTest(unittest.TestCase):

    def setUp(self):
        self.dbname = self.__class__.__name__
        self.app = flask.Flask('test')
        self.app.config['MONGO_DBNAME'] = self.dbname
        self.mongo = flask.ext.pymongo.PyMongo(self.app)
        self.mongo.cx.drop_database(self.dbname)

    def tearDown(self):
        self.mongo.cx.drop_database(self.dbname)

