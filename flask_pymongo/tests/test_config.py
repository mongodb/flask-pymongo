from __future__ import annotations

import time
from contextlib import contextmanager

import pymongo
import pytest

import flask_pymongo
from flask_pymongo.tests.util import FlaskRequestTest


class CouldNotConnect(Exception):
    pass


@contextmanager
def doesnt_raise(exc=BaseException):
    try:
        yield
    except exc:
        pytest.fail(f"{exc} was raised but should not have been")


class FlaskPyMongoConfigTest(FlaskRequestTest):
    def setUp(self):
        super().setUp()

        conn = pymongo.MongoClient(port=self.port)
        conn.test.command("ping")  # wait for server

    def tearDown(self):
        super().tearDown()

        conn = pymongo.MongoClient(port=self.port)

        conn.drop_database(self.dbname)
        conn.drop_database(self.dbname + "2")

    def test_config_with_uri_in_flask_conf_var(self):
        uri = f"mongodb://localhost:{self.port}/{self.dbname}"
        self.app.config["MONGO_URI"] = uri

        mongo = flask_pymongo.PyMongo(self.app, connect=True)

        _wait_until_connected(mongo)
        assert mongo.db.name == self.dbname
        assert ("localhost", self.port) == mongo.cx.address or (
            "127.0.0.1",
            self.port,
        ) == mongo.cx.address

    def test_config_with_uri_passed_directly(self):
        uri = f"mongodb://localhost:{self.port}/{self.dbname}"

        mongo = flask_pymongo.PyMongo(self.app, uri, connect=True)

        _wait_until_connected(mongo)
        assert mongo.db.name == self.dbname
        assert ("localhost", self.port) == mongo.cx.address or (
            "127.0.0.1",
            self.port,
        ) == mongo.cx.address

    def test_it_fails_with_no_uri(self):
        self.app.config.pop("MONGO_URI", None)

        with pytest.raises(ValueError):
            flask_pymongo.PyMongo(self.app)

    def test_multiple_pymongos(self):
        uri1 = f"mongodb://localhost:{self.port}/{self.dbname}"
        uri2 = "mongodb://localhost:{}/{}".format(self.port, self.dbname + "2")

        mongo1 = flask_pymongo.PyMongo(self.app, uri1)  # noqa: F841 unused variable
        mongo2 = flask_pymongo.PyMongo(self.app, uri2)  # noqa: F841 unused variable

        # this test passes if it raises no exceptions

    def test_custom_document_class(self):
        class CustomDict(dict):
            pass

        uri = f"mongodb://localhost:{self.port}/{self.dbname}"
        mongo = flask_pymongo.PyMongo(self.app, uri, document_class=CustomDict)
        assert mongo.db.things.find_one() is None, "precondition failed"

        mongo.db.things.insert_one({"_id": "thing", "val": "foo"})

        assert type(mongo.db.things.find_one()) is CustomDict

    def test_it_doesnt_connect_by_default(self):
        uri = f"mongodb://localhost:{self.port}/{self.dbname}"

        mongo = flask_pymongo.PyMongo(self.app, uri)

        with pytest.raises(CouldNotConnect):
            _wait_until_connected(mongo, timeout=0.2)

    def test_it_doesnt_require_db_name_in_uri(self):
        uri = f"mongodb://localhost:{self.port}"

        with doesnt_raise(Exception):
            mongo = flask_pymongo.PyMongo(self.app, uri)

        assert mongo.db is None


def _wait_until_connected(mongo, timeout=1.0):
    start = time.time()
    while time.time() < (start + timeout):
        if mongo.cx.nodes:
            return
        time.sleep(0.05)
    raise CouldNotConnect(f"could not prove mongodb connected in {timeout} seconds")
