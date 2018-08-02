from hashlib import md5
from io import BytesIO

from bson.objectid import ObjectId
from gridfs import GridFS
from werkzeug.exceptions import NotFound
import pytest

from flask_pymongo.tests.util import FlaskPyMongoTest


class GridFSCleanupMixin(object):

    def tearDown(self):
        gridfs = GridFS(self.mongo.db)
        files = list(gridfs.find())
        for gridfile in files:
            gridfs.delete(gridfile._id)

        super(GridFSCleanupMixin, self).tearDown()


class TestSaveFile(GridFSCleanupMixin, FlaskPyMongoTest):

    def test_it_saves_files(self):
        fileobj = BytesIO(b"these are the bytes")

        self.mongo.save_file("my-file", fileobj)

        gridfs = GridFS(self.mongo.db)
        assert gridfs.exists({"filename": "my-file"})

    def test_it_guesses_type_from_filename(self):
        fileobj = BytesIO(b"these are the bytes")

        self.mongo.save_file("my-file.txt", fileobj)

        gridfs = GridFS(self.mongo.db)
        gridfile = gridfs.find_one({"filename": "my-file.txt"})
        assert gridfile.content_type == "text/plain"

    def test_it_saves_files_with_props(self):
        fileobj = BytesIO(b"these are the bytes")

        self.mongo.save_file("my-file", fileobj, foo="bar")

        gridfs = GridFS(self.mongo.db)
        gridfile = gridfs.find_one({"filename": "my-file"})
        assert gridfile.foo == "bar"

    def test_it_returns_id(self):
        fileobj = BytesIO(b"these are the bytes")

        _id = self.mongo.save_file("my-file", fileobj, foo="bar")

        assert type(_id) is ObjectId


class TestSendFile(GridFSCleanupMixin, FlaskPyMongoTest):

    def setUp(self):
        super(TestSendFile, self).setUp()

        # make it bigger than 1 gridfs chunk
        self.myfile = BytesIO(b"a" * 500 * 1024)
        self.mongo.save_file("myfile.txt", self.myfile)

    def test_it_404s_for_missing_files(self):
        with pytest.raises(NotFound):
            self.mongo.send_file("no-such-file.txt")

    def test_it_sets_content_type(self):
        resp = self.mongo.send_file("myfile.txt")
        assert resp.content_type.startswith("text/plain")

    def test_it_sets_content_length(self):
        resp = self.mongo.send_file("myfile.txt")
        assert resp.content_length == len(self.myfile.getvalue())

    def test_it_sets_supports_conditional_gets(self):
        # a basic conditional GET
        environ_args = {
            "method": "GET",
            "headers": {
                "If-None-Match": md5(self.myfile.getvalue()).hexdigest(),
            },
        }

        with self.app.test_request_context(**environ_args):
            resp = self.mongo.send_file("myfile.txt")
            assert resp.status_code == 304

    def test_it_sets_cache_headers(self):
        resp = self.mongo.send_file("myfile.txt", cache_for=60)
        assert resp.cache_control.max_age == 60
        assert resp.cache_control.public is True

    def test_it_streams_results(self):
        resp = self.mongo.send_file("myfile.txt")
        assert resp.is_streamed
