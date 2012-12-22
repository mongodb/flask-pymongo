# Copyright (c) 2011, Dan Crosta
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


__all__ = ('PyMongo', 'ASCENDING', 'DESCENDING', 'PRIMARY',
           'SECONDARY', 'SECONDARY_ONLY')

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import abort, current_app, request
from gridfs import GridFS, NoFile
from mimetypes import guess_type
from pymongo import uri_parser
from werkzeug.wsgi import wrap_file
from werkzeug.routing import BaseConverter
import pymongo
import warnings

from flask_pymongo.wrappers import MongoClient
from flask_pymongo.wrappers import MongoReplicaSetClient



PRIMARY = pymongo.ReadPreference.PRIMARY
"""Send all queries to the replica set primary, and fail if none exists."""

SECONDARY = pymongo.ReadPreference.SECONDARY
"""Distribute queries among replica set secondaries unless none exist or
are up, in which case send queries to the primary."""

SECONDARY_ONLY = pymongo.ReadPreference.SECONDARY_ONLY
"""Distribute queries among replica set secondaries, and fail if none
exist."""

DESCENDING = pymongo.DESCENDING
"""Descending sort order."""

ASCENDING = pymongo.ASCENDING
"""Ascending sort order."""

READ_PREFERENCE_MAP = {
    # this handles defaulting to PRIMARY for us
    None: PRIMARY,

    # alias the string names to the correct constants
    'PRIMARY': PRIMARY,
    'SECONDARY': SECONDARY,
    'SECONDARY_ONLY': SECONDARY_ONLY,
}


class BSONObjectIdConverter(BaseConverter):
    """A simple converter for the RESTful URL routing system of Flask.

    .. code-block:: python

        @app.route('/<ObjectId:task_id>')
        def show_task(task_id):
            task = mongo.db.tasks.find_one_or_404(task_id)
            return render_template('task.html', task=task)

    It checks the validate of the id and converts it into a
    :class:`~bson.objectid.ObjectId` object. The converter will be
    automatically registered by the initialization of
    :class:`~flask_pymongo.PyMongo` with keyword :attr:`ObjectId`.
    """

    def to_python(self, value):
        try:
            return ObjectId(value)
        except InvalidId:
            raise abort(400)

    def to_url(self, value):
        return str(value)


class PyMongo(object):
    """Automatically connects to MongoDB using parameters defined in Flask
    configuration.
    """

    def __init__(self, app=None, config_prefix='MONGO'):
        if app is not None:
            self.init_app(app, config_prefix)

    def init_app(self, app, config_prefix='MONGO'):
        """Initialize the `app` for use with this :class:`~PyMongo`. This is
        called automatically if `app` is passed to :meth:`~PyMongo.__init__`.

        The app is configured according to the configuration variables
        ``PREFIX_HOST``, ``PREFIX_PORT``, ``PREFIX_DBNAME``,
        ``PREFIX_AUTO_START_REQUEST``,
        ``PREFIX_REPLICA_SET``, ``PREFIX_READ_PREFERENCE``,
        ``PREFIX_USERNAME``, ``PREFIX_PASSWORD``, and ``PREFIX_URI`` where
        "PREFIX" defaults to "MONGO". If ``PREFIX_URL`` is set, it is
        assumed to have all appropriate configurations, and the other
        keys are overwritten using their values as present in the URI.

        :param flask.Flask app: the application to configure for use with
           this :class:`~PyMongo`
        :param str config_prefix: determines the set of configuration
           variables used to configure this :class:`~PyMongo`
        """
        if 'pymongo' not in app.extensions:
            app.extensions['pymongo'] = {}

        if config_prefix in app.extensions['pymongo']:
            raise Exception('duplicate config_prefix "%s"' % config_prefix)

        self.config_prefix = config_prefix
        def key(suffix):
            return '%s_%s' % (config_prefix, suffix)

        if key('URI') in app.config:
            # bootstrap configuration from the URL
            parsed = uri_parser.parse_uri(app.config[key('URI')])
            if 'database' not in parsed:
                raise ValueError('MongoDB URI does not contain database name')
            app.config[key('DBNAME')] = parsed['database']
            app.config[key('READ_PREFERENCE')] = parsed['options'].get('read_preference')
            app.config[key('AUTO_START_REQUEST')] = parsed['options'].get('auto_start_request', True)
            app.config[key('USERNAME')] = parsed['username']
            app.config[key('PASSWORD')] = parsed['password']
            app.config[key('REPLICA_SET')] = parsed['options'].get('replica_set')
            app.config[key('MAX_POOL_SIZE')] = parsed['options'].get('max_pool_size')

            # we will use the URI for connecting instead of HOST/PORT
            app.config.pop(key('HOST'), None)
            app.config.pop(key('PORT'), None)
            host = app.config[key('URI')]

        else:
            app.config.setdefault(key('HOST'), 'localhost')
            app.config.setdefault(key('PORT'), 27017)
            app.config.setdefault(key('DBNAME'), app.name)
            app.config.setdefault(key('READ_PREFERENCE'), None)
            app.config.setdefault(key('AUTO_START_REQUEST'), True)

            # these don't have defaults
            app.config.setdefault(key('USERNAME'), None)
            app.config.setdefault(key('PASSWORD'), None)
            app.config.setdefault(key('REPLICA_SET'), None)
            app.config.setdefault(key('MAX_POOL_SIZE'), None)

            try:
                port = int(app.config[key('PORT')])
            except ValueError:
                raise TypeError('%s_PORT must be an integer' % config_prefix)

            host = '%s:%s' % (app.config[key('HOST')], app.config[key('PORT')])

        username = app.config[key('USERNAME')]
        password = app.config[key('PASSWORD')]
        auth = (username, password)

        if any(auth) and not all(auth):
            raise Exception('Must set both USERNAME and PASSWORD or neither')

        read_preference = app.config[key('READ_PREFERENCE')]
        read_preference = READ_PREFERENCE_MAP.get(read_preference, read_preference)
        if read_preference not in (PRIMARY, SECONDARY, SECONDARY_ONLY):
            raise Exception('"%s_READ_PREFERENCE" must be one of '
                            'PRIMARY, SECONDARY, SECONDARY_ONLY (was %r)'
                            % (config_prefix, read_preference))

        replica_set = app.config[key('REPLICA_SET')]
        dbname = app.config[key('DBNAME')]
        auto_start_request = app.config[key('AUTO_START_REQUEST')]
        max_pool_size = app.config[key('MAX_POOL_SIZE')]

        # document class is not supported by URI, using setdefault in all cases
        document_class = app.config.setdefault(key('DOCUMENT_CLASS'), None)

        if auto_start_request not in (True, False):
            raise TypeError('%s_AUTO_START_REQUEST must be a bool' % config_prefix)

        args = [host]
        kwargs = {
            'read_preference': read_preference,
            'tz_aware': True,
        }

        kwargs['auto_start_request'] = auto_start_request

        if replica_set is not None:
            kwargs['replicaSet'] = replica_set
            connection_cls = MongoReplicaSetClient
        else:
            connection_cls = MongoClient

        if max_pool_size is not None:
            kwargs['max_pool_size'] = max_pool_size

        if document_class is not None:
            kwargs['document_class'] = document_class

        cx = connection_cls(*args, **kwargs)
        db = cx[dbname]

        if any(auth):
            db.authenticate(username, password)

        app.extensions['pymongo'][config_prefix] = (cx, db)
        app.url_map.converters['ObjectId'] = BSONObjectIdConverter

    @property
    def cx(self):
        """The automatically created
        :class:`~flask_pymongo.wrappers.Connection` or
        :class:`~flask_pymongo.wrappers.ReplicaSetConnection`
        object.
        """
        if self.config_prefix not in current_app.extensions['pymongo']:
            raise Exception('not initialized. did you forget to call init_app?')
        return current_app.extensions['pymongo'][self.config_prefix][0]

    @property
    def db(self):
        """The automatically created
        :class:`~flask_pymongo.wrappers.Database` object
        corresponding to the provided ``MONGO_DBNAME`` configuration
        parameter.
        """
        if self.config_prefix not in current_app.extensions['pymongo']:
            raise Exception('not initialized. did you forget to call init_app?')
        return current_app.extensions['pymongo'][self.config_prefix][1]

    # view helpers
    def send_file(self, filename, base='fs', version=-1, cache_for=31536000):
        """Return an instance of the :attr:`~flask.Flask.response_class`
        containing the named file, and implement conditional GET semantics
        (using :meth:`~werkzeug.wrappers.ETagResponseMixin.make_conditional`).

        .. code-block:: python

            @app.route('/uploads/<path:filename>')
            def get_upload(filename):
                return mongo.send_file(filename)

        :param str filename: the filename of the file to return
        :param str base: the base name of the GridFS collections to use
        :param bool version: if positive, return the Nth revision of the file
           identified by filename; if negative, return the Nth most recent
           revision. If no such version exists, return with HTTP status 404.
        :param int cache_for: number of seconds that browsers should be
           instructed to cache responses
        """
        if not isinstance(base, (str, unicode)):
            raise TypeError('"base" must be string or unicode')
        if not isinstance(version, (int, long)):
            raise TypeError('"version" must be an integer')
        if not isinstance(cache_for, (int, long)):
            raise TypeError('"cache_for" must be an integer')

        storage = GridFS(self.db, base)

        try:
            fileobj = storage.get_version(filename=filename, version=version)
        except NoFile:
            abort(404)


        # mostly copied from flask/helpers.py, with
        # modifications for GridFS
        data = wrap_file(request.environ, fileobj, buffer_size=1024 * 256)
        response = current_app.response_class(
            data,
            mimetype=fileobj.content_type,
            direct_passthrough=True)
        response.content_length = fileobj.length
        response.last_modified = fileobj.upload_date
        response.set_etag(fileobj.md5)
        response.cache_control.max_age = cache_for
        response.cache_control.s_max_age = cache_for
        response.cache_control.public = True
        response.make_conditional(request)
        return response

    def save_file(self, filename, fileobj, base='fs', content_type=None):
        """Save the file-like object to GridFS using the given filename.
        Returns ``None``.

        .. code-block:: python

            @app.route('/uploads/<path:filename>', methods=['POST'])
            def save_upload(filename):
                mongo.save_file(filename, request.files['file'])
                return redirect(url_for('get_upload', filename=filename))

        :param str filename: the filename of the file to return
        :param file fileobj: the file-like object to save
        :param str base: base the base name of the GridFS collections to use
        :param str content_type: the MIME content-type of the file. If
           ``None``, the content-type is guessed from the filename using
           :func:`~mimetypes.guess_type`
        """
        if not isinstance(base, (str, unicode)):
            raise TypeError('"base" must be string or unicode')
        if not (hasattr(fileobj, 'read') and callable(fileobj.read)):
            raise TypeError('"fileobj" must have read() method')

        if content_type is None:
            content_type, _ = guess_type(filename)

        storage = GridFS(self.db, base)
        storage.put(fileobj, filename=filename, content_type=content_type)
