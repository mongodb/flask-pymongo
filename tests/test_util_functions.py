from tests import util

from flask import Flask, jsonify
from flask_pymongo import bson_to_json
from bson import BSON


class BsonJsonifyTest(util.FlaskRequestTest):

    def setUp(self):
        self.app = Flask('test')
        self.context = self.app.test_request_context('/')
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def test_jsonify_bson_object(self):
        bson_obj = BSON.encode({'a': 1})
        assert bson_to_json(bson_obj) == jsonify(a=1)
