from __future__ import annotations

import unittest

import flask

import flask_pymongo


class FlaskRequestTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.dbname = self.__class__.__name__
        self.app = flask.Flask("test")
        self.context = self.app.test_request_context("/")
        self.context.push()
        self.port = 27017

    def tearDown(self):
        super().tearDown()

        self.context.pop()


class FlaskPyMongoTest(FlaskRequestTest):
    def setUp(self):
        super().setUp()

        uri = f"mongodb://localhost:{self.port}/{self.dbname}"
        self.mongo = flask_pymongo.PyMongo(self.app, uri)

    def tearDown(self):
        self.mongo.cx.drop_database(self.dbname)

        super().tearDown()
