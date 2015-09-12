import sys
import datetime

from tests import util

from flask import Flask, jsonify as flask_jsonify
from flask.ext.pymongo import jsonify
from bson import ObjectId, Binary, Code, Regex, DBRef


if sys.version_info[0] == 2:
    str = unicode


class BsonJsonifyTest(util.FlaskRequestTest):

    def setUp(self):
        self.app = Flask('test')
        self.context = self.app.test_request_context('/')
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def test_jsonify_ObjectId(self):
        objectid = ObjectId(b'foo-bar-quuz')
        json = {'a': 1, 'id_': objectid}
        safe_json = {'a': 1, 'id_': {'$oid': str(objectid)}}

        jsonified_bson = jsonify(json).response
        jsonified = flask_jsonify(safe_json).response

        assert jsonified_bson == jsonified

    def test_jsonify_Binary(self):
        binary = Binary(b"hello")
        json = {'a': 1, 'bin': binary}
        safe_json = {'a': 1, 'bin': {'$binary': "aGVsbG8=", "$type": "00"}}

        jsonified_bson = jsonify(json).response
        jsonified = flask_jsonify(safe_json).response

        assert jsonified_bson == jsonified

    def test_jsonify_Code(self):
        code = Code("function () { console.log('Hello, world!'); }();")
        json = {'a': 1, 'code': code}
        safe_json = {'a': 1, 'code': {'$code': str(code), '$scope': {}}}

        jsonified_bson = jsonify(json).response
        jsonified = flask_jsonify(safe_json).response

        assert jsonified_bson == jsonified

    def test_jsonify_Regex(self):
        regex = Regex("bb|[^b]{2}")
        json = {'a': 1, 'regex': regex}
        safe_json = {'a': 1, 'regex': {'$regex': "bb|[^b]{2}", "$options": ""}}

        jsonified_bson = jsonify(json).response
        jsonified = flask_jsonify(safe_json).response

        assert jsonified_bson == jsonified

    def test_jsonify_DBRef(self):
        dbref = DBRef("fake_document", "helloworld")
        json = {'a': 1, 'dbref': dbref}
        safe_json = {
            'a': 1,
            'dbref': {
                '$id': 'helloworld',
                '$ref': 'fake_document'
            }
        }

        jsonified_bson = jsonify(json).response
        jsonified = flask_jsonify(safe_json).response

        assert jsonified_bson == jsonified
