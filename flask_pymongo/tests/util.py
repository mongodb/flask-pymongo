import os

import flask
import flask_pymongo
import unittest


class ToxDockerMixin(object):
    """
    Check for the environment var from tox-docker describing the port, and set :attr:`port`.
    """

    def setUp(self):
        super(ToxDockerMixin, self).setUp()

        self.port = int(os.environ.get("MONGO_27017_TCP", 27017))


class FlaskRequestTest(ToxDockerMixin, unittest.TestCase):

    def setUp(self):
        super(FlaskRequestTest, self).setUp()

        self.dbname = self.__class__.__name__
        self.app = flask.Flask("test")
        self.context = self.app.test_request_context("/")
        self.context.push()

    def tearDown(self):
        super(FlaskRequestTest, self).tearDown()

        self.context.pop()

class FlaskPyMongoTest(FlaskRequestTest):

    def setUp(self):
        super(FlaskPyMongoTest, self).setUp()

        uri = "mongodb://localhost:{}/{}".format(self.port, self.dbname)
        self.mongo = flask_pymongo.PyMongo(self.app, uri)

    def tearDown(self):
        self.mongo.cx.drop_database(self.dbname)

        super(FlaskPyMongoTest, self).tearDown()
