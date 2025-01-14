from __future__ import annotations

from bson import ObjectId
from werkzeug.exceptions import NotFound
from werkzeug.routing.map import Map

from flask_pymongo import BSONObjectIdConverter

from .util import FlaskPyMongoTest


class UrlConverterTest(FlaskPyMongoTest):
    def test_bson_object_id_converter(self):
        converter = BSONObjectIdConverter(Map())

        self.assertRaises(NotFound, converter.to_python, ("132"))
        assert converter.to_python("4e4ac5cfffc84958fa1f45fb") == ObjectId(
            "4e4ac5cfffc84958fa1f45fb"
        )
        assert converter.to_url(ObjectId("4e4ac5cfffc84958fa1f45fb")) == "4e4ac5cfffc84958fa1f45fb"
