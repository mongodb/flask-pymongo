from bson import ObjectId
from werkzeug.exceptions import NotFound

from flask_pymongo import BSONObjectIdConverter
from flask_pymongo.tests.util import FlaskPyMongoTest


class UrlConverterTest(FlaskPyMongoTest):

    def test_bson_object_id_converter(self):
        converter = BSONObjectIdConverter("/")

        self.assertRaises(NotFound, converter.to_python, ("132"))
        assert converter.to_python("4e4ac5cfffc84958fa1f45fb") == \
            ObjectId("4e4ac5cfffc84958fa1f45fb")
        assert converter.to_url(ObjectId("4e4ac5cfffc84958fa1f45fb")) == \
            "4e4ac5cfffc84958fa1f45fb"
