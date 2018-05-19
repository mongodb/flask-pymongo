from util import FlaskRequestTest, FlaskPyMongoTest

import time
import os
import unittest

import pymongo
import flask
import flask_pymongo
import warnings


PYMONGO_VERSION = tuple(map(int, pymongo.version.split(".")))


class CustomDict(dict):
    pass


class FlaskPyMongoConfigTest(FlaskRequestTest):

    def setUp(self):
        super(FlaskPyMongoConfigTest, self).setUp()

        conn = pymongo.MongoClient(port=self.port)
        conn.test_db.command(
            "createUser",
            "flask",
            pwd="pymongo",
            roles=["readWrite"],
        )

    def tearDown(self):
        super(FlaskPyMongoConfigTest, self).tearDown()

        conn = pymongo.MongoClient(port=self.port)
        conn.test_db.command("dropUser", "flask")

    def test_default_config_prefix(self):
        self.app.config['MONGO_DBNAME'] = 'flask_pymongo_test_db'
        self.app.config['MONGO_HOST'] = 'localhost'
        self.app.config['MONGO_PORT'] = self.port

        mongo = flask_pymongo.PyMongo(self.app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        if pymongo.version_tuple[0] > 2:
            time.sleep(0.2)
            assert ('localhost', self.port) == mongo.cx.address
        else:
            assert mongo.cx.host == 'localhost'
            assert mongo.cx.port == self.port

    def test_custom_config_prefix(self):
        self.app.config['CUSTOM_DBNAME'] = 'flask_pymongo_test_db'
        self.app.config['CUSTOM_HOST'] = 'localhost'
        self.app.config['CUSTOM_PORT'] = self.port

        mongo = flask_pymongo.PyMongo(self.app, 'CUSTOM')
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        if pymongo.version_tuple[0] > 2:
            time.sleep(0.2)
            assert ('localhost', self.port) == mongo.cx.address
        else:
            assert mongo.cx.host == 'localhost'
            assert mongo.cx.port == self.port

    def test_converts_str_to_int(self):
        self.app.config['MONGO_DBNAME'] = 'flask_pymongo_test_db'
        self.app.config['MONGO_HOST'] = 'localhost'
        self.app.config['MONGO_PORT'] = str(self.port)

        mongo = flask_pymongo.PyMongo(self.app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        if pymongo.version_tuple[0] > 2:
            time.sleep(0.2)
            assert ('localhost', self.port) == mongo.cx.address
        else:
            assert mongo.cx.host == 'localhost'
            assert mongo.cx.port == self.port

    def test_rejects_invalid_string(self):
        self.app.config['MONGO_PORT'] = '27017x'

        self.assertRaises(TypeError, flask_pymongo.PyMongo, self.app)

    def test_multiple_pymongos(self):
        for prefix in ('ONE', 'TWO'):
            self.app.config['%s_PORT' % prefix] = self.port
            self.app.config['%s_DBNAME' % prefix] = prefix

        for prefix in ('ONE', 'TWO'):
            flask_pymongo.PyMongo(self.app, config_prefix=prefix)

            # this test passes if it raises no exceptions

    def test_config_with_uri(self):
        self.app.config['MONGO_URI'] = 'mongodb://localhost:{}/flask_pymongo_test_db'.format(self.port)

        with warnings.catch_warnings():
            # URI connections without a username and password
            # work, but warn that auth should be supplied
            warnings.simplefilter('ignore')
            mongo = flask_pymongo.PyMongo(self.app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        if pymongo.version_tuple[0] > 2:
            time.sleep(0.2)
            assert ('localhost', self.port) == mongo.cx.address
        else:
            assert mongo.cx.host == 'localhost'
            assert mongo.cx.port == self.port

    @unittest.skip("URI without port won't work with tox-docker's non-default port")
    def test_config_with_uri_no_port(self):
        self.app.config['MONGO_URI'] = 'mongodb://localhost/flask_pymongo_test_db'

        with warnings.catch_warnings():
            # URI connections without a username and password
            # work, but warn that auth should be supplied
            warnings.simplefilter('ignore')
            mongo = flask_pymongo.PyMongo(self.app)
        assert mongo.db.name == 'flask_pymongo_test_db', 'wrong dbname: %s' % mongo.db.name
        if pymongo.version_tuple[0] > 2:
            time.sleep(0.2)
            assert ('localhost', self.port) == mongo.cx.address
        else:
            assert mongo.cx.host == 'localhost'
            assert mongo.cx.port == self.port

    def test_config_with_document_class(self):
        self.app.config['MONGO_PORT'] = self.port
        self.app.config['MONGO_DOCUMENT_CLASS'] = CustomDict
        mongo = flask_pymongo.PyMongo(self.app)
        if pymongo.version_tuple[0] > 2:
            assert mongo.cx.codec_options.document_class == CustomDict
        else:
            assert mongo.cx.document_class == CustomDict

    def test_config_without_document_class(self):
        self.app.config['MONGO_PORT'] = self.port
        mongo = flask_pymongo.PyMongo(self.app)
        if pymongo.version_tuple[0] > 2:
            assert mongo.cx.codec_options.document_class == dict
        else:
            assert mongo.cx.document_class == dict

    def test_host_with_port_does_not_get_overridden_by_separate_port_config_value(self):
        self.app.config['MONGO_HOST'] = 'localhost:{}'.format(self.port)
        self.app.config['MONGO_PORT'] = 27018

        with warnings.catch_warnings():
            # URI connections without a username and password
            # work, but warn that auth should be supplied
            warnings.simplefilter('ignore')
            mongo = flask_pymongo.PyMongo(self.app)
        if pymongo.version_tuple[0] > 2:
            time.sleep(0.2)
            assert ('localhost', self.port) == mongo.cx.address
        else:
            assert mongo.cx.host == 'localhost'
            assert mongo.cx.port == self.port

    def test_uri_prioritised_over_host_and_port(self):
        self.app.config['MONGO_URI'] = 'mongodb://localhost:{}/database_name'.format(self.port)
        self.app.config['MONGO_HOST'] = 'some_other_host'
        self.app.config['MONGO_PORT'] = 27018
        self.app.config['MONGO_DBNAME'] = 'not_the_correct_db_name'

        with warnings.catch_warnings():
            # URI connections without a username and password
            # work, but warn that auth should be supplied
            warnings.simplefilter('ignore')
            mongo = flask_pymongo.PyMongo(self.app)
        if pymongo.version_tuple[0] > 2:
            time.sleep(0.2)
            assert ('localhost', self.port) == mongo.cx.address
        else:
            assert mongo.cx.host == 'localhost'
            assert mongo.cx.port == self.port
        assert mongo.db.name == 'database_name'


    @unittest.skipIf(PYMONGO_VERSION < (2, 8), "missing auth mechanism causes exceptions in older pymongos")
    def test_missing_auth_mechanism_in_nonprefixed_config(self):
        self.app.config["MONGO_HOST"] = 'localhost'
        self.app.config["MONGO_PORT"] = self.port
        self.app.config["MONGO_USERNAME"] = 'flask'
        self.app.config["MONGO_PASSWORD"] = 'pymongo'
        self.app.config['MONGO_DBNAME'] = 'test_db'

        mongo = flask_pymongo.PyMongo(self.app)

        assert mongo.db.name == 'test_db', 'wrong dbname: %s' % mongo.db.name

        if pymongo.version_tuple[0] > 2:
            time.sleep(0.2)

            assert ('localhost', self.port) == mongo.cx.address
        else:
            assert mongo.cx.host == 'localhost'
            assert mongo.cx.port == self.port


    @unittest.skipIf(PYMONGO_VERSION < (2, 8), "missing auth mechanism causes exceptions in older pymongos")
    def test_missing_auth_mechanism_in_prefixed_config(self):
        self.app.config["CUSTOM_MONGO_HOST"] = 'localhost'
        self.app.config["CUSTOM_MONGO_PORT"] = self.port
        self.app.config["CUSTOM_MONGO_USERNAME"] = 'flask'
        self.app.config["CUSTOM_MONGO_PASSWORD"] = 'pymongo'
        self.app.config['CUSTOM_MONGO_DBNAME'] = 'test_db'

        mongo = flask_pymongo.PyMongo(self.app, 'CUSTOM_MONGO')

        assert mongo.db.name == 'test_db', 'wrong dbname: %s' % mongo.db.name

        if pymongo.version_tuple[0] > 2:
            time.sleep(0.2)

            assert ('localhost', self.port) == mongo.cx.address
        else:
            assert mongo.cx.host == 'localhost'
            assert mongo.cx.port == self.port




class CustomDocumentClassTest(FlaskPyMongoTest):
    """ Class that tests reading from DB with custom document_class """

    def test_create_with_document_class(self):
        """ This test doesn't use self.mongo, because it has to change config

        It uses second mongo connection, using a CUSTOM prefix to avoid
        duplicate config_prefix exception. To make use of tearDown and thus DB
        deletion even in case of failure, it uses same DBNAME.

        """
        # copying standard DBNAME, so this DB gets also deleted by tearDown
        self.app.config['CUSTOM_DBNAME'] = self.app.config['MONGO_DBNAME']
        self.app.config['CUSTOM_DOCUMENT_CLASS'] = CustomDict
        self.app.config['CUSTOM_PORT'] = self.port
        # not using self.mongo, because we want to use updated config
        # also using CUSTOM, to avoid duplicate config_prefix exception
        mongo = flask_pymongo.PyMongo(self.app, 'CUSTOM')
        assert mongo.db.things.find_one() is None
        # write document and retrieve, to check if type is really CustomDict
        if pymongo.version_tuple[0] > 2:
            # Write Concern is set to w=1 by default in pymongo > 3.0
            mongo.db.things.insert_one({'_id': 'thing', 'val': 'foo'})
        else:
            mongo.db.things.insert({'_id': 'thing', 'val': 'foo'}, w=1)
        assert type(mongo.db.things.find_one()) == CustomDict

    def test_create_without_document_class(self):
        """ This uses self.mongo, which uses config without document_class """
        assert self.mongo.db.things.find_one() is None
        # write document and retrieve, to check if type is dict (default)
        if pymongo.version_tuple[0] > 2:
            # Write Concern is set to w=1 by default in pymongo > 3.0
            self.mongo.db.things.insert_one({'_id': 'thing', 'val': 'foo'})
        else:
            self.mongo.db.things.insert({'_id': 'thing', 'val': 'foo'}, w=1)
        assert type(self.mongo.db.things.find_one()) == dict
