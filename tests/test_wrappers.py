from tests import util
from werkzeug.exceptions import HTTPException

class CollectionTest(util.FlaskPyMongoTest):

    def test_find_one_or_404(self):
        self.mongo.db.things.remove()

        try:
            self.mongo.db.things.find_one_or_404({'_id': 'thing'})
        except HTTPException as notfound:
            assert notfound.code == 404, "raised wrong exception"

        self.mongo.db.things.insert({'_id': 'thing', 'val': 'foo'}, safe=True)

        # now it should not raise
        thing = self.mongo.db.things.find_one_or_404({'_id': 'thing'})
        assert thing['val'] == 'foo', 'got wrong thing'


        # also test with dotted-named collections
        self.mongo.db.things.morethings.remove()
        try:
            self.mongo.db.things.morethings.find_one_or_404({'_id': 'thing'})
        except HTTPException as notfound:
            assert notfound.code == 404, "raised wrong exception"

        self.mongo.db.things.morethings.insert({'_id': 'thing', 'val': 'foo'}, safe=True)

        # now it should not raise
        thing = self.mongo.db.things.morethings.find_one_or_404({'_id': 'thing'})
        assert thing['val'] == 'foo', 'got wrong thing'
