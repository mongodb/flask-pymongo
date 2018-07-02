# Copyright (c) 2011-2017, Dan Crosta
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from flask import abort
from pymongo import collection
from pymongo import database
from pymongo import mongo_client


class MongoClient(mongo_client.MongoClient):

    """Wrapper for :class:`~pymongo.mongo_client.MongoClient`.

    Returns instances of Flask-PyMongo
    :class:`~flask_pymongo.wrappers.Database` instead of native PyMongo
    :class:`~pymongo.database.Database` when accessed with dot notation.

    """

    def __getattr__(self, name):  # noqa: D105
        attr = super(MongoClient, self).__getattr__(name)
        if isinstance(attr, database.Database):
            return Database(self, name)
        return attr

    def __getitem__(self, item):  # noqa: D105
        attr = super(MongoClient, self).__getitem__(item)
        if isinstance(attr, database.Database):
            return Database(self, item)
        return attr


class Database(database.Database):

    """Wrapper for :class:`~pymongo.database.Database`.

    Returns instances of Flask-PyMongo
    :class:`~flask_pymongo.wrappers.Collection` instead of native PyMongo
    :class:`~pymongo.collection.Collection` when accessed with dot notation.

    """

    def __getattr__(self, name):  # noqa: D105
        attr = super(Database, self).__getattr__(name)
        if isinstance(attr, collection.Collection):
            return Collection(self, name)
        return attr

    def __getitem__(self, item):  # noqa: D105
        item_ = super(Database, self).__getitem__(item)
        if isinstance(item_, collection.Collection):
            return Collection(self, item)
        return item_


class Collection(collection.Collection):

    """Sub-class of PyMongo :class:`~pymongo.collection.Collection` with helpers.

    """

    def __getattr__(self, name):  # noqa: D105
        attr = super(Collection, self).__getattr__(name)
        if isinstance(attr, collection.Collection):
            db = self._Collection__database
            return Collection(db, attr.name)
        return attr

    def __getitem__(self, item):  # noqa: D105
        item_ = super(Collection, self).__getitem__(item)
        if isinstance(item_, collection.Collection):
            db = self._Collection__database
            return Collection(db, item_.name)
        return item_

    def find_one_or_404(self, *args, **kwargs):
        """Find a single document or raise a 404.

        This is like :meth:`~pymongo.collection.Collection.find_one`, but
        rather than returning ``None``, cause a 404 Not Found HTTP status
        on the request.

        .. code-block:: python

            @app.route("/user/<username>")
            def user_profile(username):
                user = mongo.db.users.find_one_or_404({"_id": username})
                return render_template("user.html",
                    user=user)

        """
        found = self.find_one(*args, **kwargs)
        if found is None:
            abort(404)
        return found
