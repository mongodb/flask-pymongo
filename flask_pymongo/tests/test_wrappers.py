from werkzeug.exceptions import HTTPException

from flask_pymongo.tests.util import FlaskPyMongoTest


class CollectionTest(FlaskPyMongoTest):

    def test_find_one_or_404(self):
        self.mongo.db.things.delete_many({})

        try:
            self.mongo.db.things.find_one_or_404({"_id": "thing"})
        except HTTPException as notfound:
            assert notfound.code == 404, "raised wrong exception"

        self.mongo.db.things.insert_one({"_id": "thing", "val": "foo"})

        # now it should not raise
        thing = self.mongo.db.things.find_one_or_404({"_id": "thing"})
        assert thing["val"] == "foo", "got wrong thing"

        # also test with dotted-named collections
        self.mongo.db.things.morethings.delete_many({})
        try:
            self.mongo.db.things.morethings.find_one_or_404({"_id": "thing"})
        except HTTPException as notfound:
            assert notfound.code == 404, "raised wrong exception"

        self.mongo.db.things.morethings.insert_one({"_id": "thing", "val": "foo"})

        # now it should not raise
        thing = self.mongo.db.things.morethings.find_one_or_404({"_id": "thing"})
        assert thing["val"] == "foo", "got wrong thing"
