from __future__ import annotations

import json

from bson import ObjectId
from flask import jsonify

from flask_pymongo.tests.util import FlaskPyMongoTest


class JSONTest(FlaskPyMongoTest):
    def test_it_encodes_json(self):
        resp = jsonify({"foo": "bar"})
        dumped = json.loads(resp.get_data().decode("utf-8"))
        self.assertEqual(dumped, {"foo": "bar"})

    def test_it_handles_pymongo_types(self):
        resp = jsonify({"id": ObjectId("5cf29abb5167a14c9e6e12c4")})
        dumped = json.loads(resp.get_data().decode("utf-8"))
        self.assertEqual(dumped, {"id": {"$oid": "5cf29abb5167a14c9e6e12c4"}})

    def test_it_jsonifies_a_cursor(self):
        self.mongo.db.rows.insert_many([{"foo": "bar"}, {"foo": "baz"}])

        curs = self.mongo.db.rows.find(projection={"_id": False}).sort("foo")

        resp = jsonify(curs)
        dumped = json.loads(resp.get_data().decode("utf-8"))
        self.assertEqual([{"foo": "bar"}, {"foo": "baz"}], dumped)
