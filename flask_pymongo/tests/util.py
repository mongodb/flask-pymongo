import os
import unittest

import flask

import flask_pymongo


class ToxDockerMixin(object):

    """
    Sets :attr:`port` based on the env var from tox-docker, if present.
    """

    def setUp(self):
        super(ToxDockerMixin, self).setUp()

        # tox-docker could be running any version; find the env
        # var that looks like what tox-docker would provide, but
        # fail if there are more than one
        env_vars = [
            (k, v)
            for k, v in os.environ.items()
            if k.startswith("MONGO") and k.endswith("_TCP_PORT")
        ]

        self.port = 27017
        if len(env_vars) == 1:
            self.port = int(env_vars[0][1])
        else:
            self.fail(
                f"too many tox-docker mongo port env vars (found {len(env_vars)})",
            )


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
