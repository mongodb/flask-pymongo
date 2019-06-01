# Copyright (c) 2011-2019, Dan Crosta
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


__all__ = ("BSONObjectIdConverter", "JSONEncoder")

from bson import json_util, SON
from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import abort, json as flask_json
from six import iteritems, string_types
from werkzeug.routing import BaseConverter
import pymongo

if pymongo.version_tuple >= (3, 5, 0):
    from bson.json_util import RELAXED_JSON_OPTIONS
    DEFAULT_JSON_OPTIONS = RELAXED_JSON_OPTIONS
else:
    DEFAULT_JSON_OPTIONS = None


def _iteritems(obj):
    if hasattr(obj, "iteritems"):
        return obj.iteritems()
    elif hasattr(obj, "items"):
        return obj.items()
    else:
        raise TypeError("{!r} missing iteritems() and items()".format(obj))


class BSONObjectIdConverter(BaseConverter):

    """A simple converter for the RESTful URL routing system of Flask.

    .. code-block:: python

        @app.route("/<ObjectId:task_id>")
        def show_task(task_id):
            task = mongo.db.tasks.find_one_or_404(task_id)
            return render_template("task.html", task=task)

    Valid object ID strings are converted into
    :class:`~bson.objectid.ObjectId` objects; invalid strings result
    in a 404 error. The converter is automatically registered by the
    initialization of :class:`~flask_pymongo.PyMongo` with keyword
    :attr:`ObjectId`.

    The :class:`~flask_pymongo.helpers.BSONObjectIdConverter` is
    automatically installed on the :class:`~flask_pymongo.PyMongo`
    instnace at creation time.

    """

    def to_python(self, value):
        try:
            return ObjectId(value)
        except InvalidId:
            raise abort(404)

    def to_url(self, value):
        return str(value)


class JSONEncoder(flask_json.JSONEncoder):

    """A JSON encoder that uses :mod:`bson.json_util` for MongoDB documents.

    .. code-block:: python

        @app.route("/cart/<ObjectId:cart_id>")
        def json_route(cart_id):
            results = mongo.db.carts.find({"_id": cart_id})
            return jsonify(results)

        # returns a Response with JSON body and application/json content-type:
        # '[{"count":12,"item":"egg"},{"count":1,"item":"apple"}]'

    Since this uses PyMongo's JSON tools, certain types may serialize
    differently than you expect. See :class:`~bson.json_util.JSONOptions`
    for details on the particular serialization that will be used.

    A :class:`~flask_pymongo.helpers.JSONEncoder` is automatically
    automatically installed on the :class:`~flask_pymongo.PyMongo`
    instance at creation time, using
    :const:`~bson.json_util.RELAXED_JSON_OPTIONS`. You can change the
    :class:`~bson.json_util.JSONOptions` in use by passing
    ``json_options`` to the :class:`~flask_pymongo.PyMongo`
    constructor.

    .. note::

        :class:`~bson.json_util.JSONOptions` is only supported as of
        PyMongo version 3.4. For older versions of PyMongo, you will
        have less control over the JSON format that results from calls
        to :func:`~flask.json.jsonify`.

    .. versionadded:: 2.4.0

    """

    def __init__(self, json_options, *args, **kwargs):
        if json_options is None:
            json_options = DEFAULT_JSON_OPTIONS
        if json_options is not None:
            self._default_kwargs = {"json_options": json_options}
        else:
            self._default_kwargs = {}

        super(JSONEncoder, self).__init__(*args, **kwargs)

    def default(self, obj):
        """Serialize MongoDB object types using :mod:`bson.json_util`.

        Falls back to Flask's default JSON serialization for all other types.

        This may raise ``TypeError`` for object types not recignozed.

        .. versionadded:: 2.4.0

        """
        if hasattr(obj, "iteritems") or hasattr(obj, "items"):
            return SON((k, self.default(v)) for k, v in iteritems(obj))
        elif hasattr(obj, "__iter__") and not isinstance(obj, string_types):
            return [self.default(v) for v in obj]
        else:
            try:
                return json_util.default(obj, **self._default_kwargs)
            except TypeError:
                # PyMongo couldn't convert into a serializable object, and
                # the Flask default JSONEncoder won't; so we return the
                # object itself and let stdlib json handle it if possible
                return obj
