from tests import util
from werkzeug.exceptions import HTTPException

import pymongo

class CollectionTest(util.FlaskPyMongoTest):

    def test_find_one_or_404(self):
        self.mongo.db.things.remove()

        try:
            self.mongo.db.things.find_one_or_404({'_id': 'thing'})
        except HTTPException as notfound:
            assert notfound.code == 404, "raised wrong exception"

        if pymongo.version_tuple[0] > 2:
            self.mongo.db.things.insert_one({'_id': 'thing', 'val': 'foo'})
        else:
            self.mongo.db.things.insert({'_id': 'thing', 'val': 'foo'}, w=1)

        # now it should not raise
        thing = self.mongo.db.things.find_one_or_404({'_id': 'thing'})
        assert thing['val'] == 'foo', 'got wrong thing'

        # also test with dotted-named collections
        self.mongo.db.things.morethings.remove()
        try:
            self.mongo.db.things.morethings.find_one_or_404({'_id': 'thing'})
        except HTTPException as notfound:
            assert notfound.code == 404, "raised wrong exception"

        if pymongo.version_tuple[0] > 2:
            # Write Concern is set to w=1 by default in pymongo > 3.0
            self.mongo.db.things.morethings.insert_one({'_id': 'thing', 'val': 'foo'})
        else:
            self.mongo.db.things.morethings.insert({'_id': 'thing', 'val': 'foo'}, w=1)

        # now it should not raise
        thing = self.mongo.db.things.morethings.find_one_or_404({'_id': 'thing'})
        assert thing['val'] == 'foo', 'got wrong thing'
