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

__version_info__ = (0, 1, 0)
__version__ = '.'.join(str(i) for i in __version_info__)

__all__ = ('PyMongo', 'ASCENDING', 'DESCENDING', 'PRIMARY',
           'SECONDARY', 'SECONDARY_ONLY')


from flask import abort, request
from gridfs import GridFS, NoFile
from mimetypes import guess_type
from pymongo import (Connection, ReadPreference, ReplicaSetConnection,
                     ASCENDING, DESCENDING)
from pymongo.collection import Collection
from werkzeug.wsgi import wrap_file

from flask_pymongo.util import monkey_patch



PRIMARY = ReadPreference.PRIMARY
"""Send all queries to the replica set primary, and fail if none exists."""

SECONDARY = ReadPreference.SECONDARY
"""Distribute queries among replica set secondaries unless none exist or
are up, in which case send queries to the primary."""

SECONDARY_ONLY = ReadPreference.SECONDARY_ONLY
"""Distribute queries among replica set secondaries, and fail if none
exist."""


class PyMongo(object):
    """Automatically connects to MongoDB using parameters defined in Flask
    configuration named ``MONGO_HOST``, ``MONGO_PORT``, and ``MONGO_DBNAME``.

    .. py:attribute:: cx

       The automatically created :class:`~pymongo.connection.Connection`
       object.

    .. py:attribute:: db

       The automatically created :class:`~pymongo.database.Database`
       object corresponding to the provided ``MONGO_DBNAME`` configuration
       parameter.
    """

    def __init__(self, app, config_prefix='MONGO'):
        self.app = app
        self.config_prefix = config_prefix

        self.host = self._get_config('HOST', 'localhost')
        self.port = self._get_config('PORT', 27017)
        dbname = self._get_config('DBNAME')
        # TODO: authentication

        try:
            self.port = int(self.port)
        except ValueError:
            raise TypeError('%s_PORT must be an integer' % config_prefix)

        if not dbname:
            dbname = app.name

        self.cx = self.connect()
        self.db = self.cx[dbname]

        self.setup_hooks()

    def _get_config(self, suffix, default=None):
        varname = '%s_%s' % (self.config_prefix, suffix)
        return self.app.config.get(varname, default)

    def connect(self):
        """Sub-classes may override this to return a specific type of
        connection, or to modify the connection in some way.
        """
        return Connection(
            host=self.host,
            port=self.port,
        )

    def setup_hooks(self):
        """Sub-classes may override this to set up specific pre- and
        post-request hooks as needed.

        This implementation adds a :meth:`~flask.Flask.after_request`
        hook which calls :meth:`~pymongo.connection.Connection.end_request`.
        """
        self.app.after_request(self._after_request)

    def _after_request(self, response):
        self.cx.end_request()
        return response

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
        :param str base: base the base name of the GridFS collections to use
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
        data = wrap_file(request.environ, fileobj, buffer_size=1024*256)
        response = self.app.response_class(
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


    # monkey patches
    @monkey_patch(Collection)
    def find_one_or_404(self, *args, **kwargs):
        """This method is monkey-patched onto
        :class:`pymongo.collection.Collection` when Flask-PyMongo is imported.

        Find and return a single document, or trigger a 404 Not Found exception
        if no document matches the query spec. See
        :meth:`~pymongo.collection.Collection.find_one` for details.

        .. code-block:: python

            @app.route('/user/<username>')
            def user_profile(username):
                user = mongo.db.users.find_one_or_404({'_id': username})
                return render_template('user.html',
                    user=user)

        :param spec_or_id: what to find, either a dictionary which is
           used as a query, or an instance which is used as a query
           for ``_id``
        :param args: additional positional arguments to
           :meth:`~pymongo.collection.Collection.find_one`
        :param kwargs: additional keyword arguments to
           :meth:`~pymongo.collection.Collection.find_one`
        """
        found = self.find_one(*args, **kwargs)
        if not found:
            abort(404)
        return found

class PyMongoReplicaSet(PyMongo):
    """This sub-class of :class:`~flask_pymongo.PyMongo` establishes a
    connection to a replica set instead of to a single ``mongod`` server.

    It requires that the ``MONGO_REPLSET`` configuration variable match the
    replica set name of the members it connects to, and optionally takes a
    ``MONGO_READPREF`` configuration variable (default:
    :data:`~flask_pymongo.PRIMARY`) to configure how reads are routed to
    the replica set members.
    """

    __read_pref_map = {
        # this handles defaulting to PRIMARY for us
        None: PRIMARY,

        # alias the string names to the correct constants
        'PRIMARY': PRIMARY,
        'SECONDARY': SECONDARY,
        'SECONDARY_ONLY': SECONDARY_ONLY,
    }

    def connect(self):
        """Overrides :meth:`~PyMongo.connect` to create a
        :class:`~pymongo.replica_set_connection.ReplicaSetConnection` instead.


        """
        replset_name = self._get_config('REPLSET')
        if not replset_name:
            # TODO: better exception
            raise Exception('PyMongoReplicaSet requires "%s_REPLSET"'
                            % self.config_prefix)

        read_pref = self._get_config('READPREF')
        read_pref = self.__read_pref_map.get(read_pref, read_pref)
        if read_pref not in (PRIMARY, SECONDARY, SECONDARY_ONLY):
            raise ValueError('"%s_READPREF" must be one of ReadPreference.PRIMARY, '
                             'ReadPreference.SECONDARY, or ReadPreference.SECONDARY_ONLY'
                             % self._config_prefix)

        return ReplicaSetConnection(
            '%s:%d' % (self.host, self.port),
            replicaSet=replset_name,
            read_preference=read_pref,
        )

    def setup_hooks(self):
        """Does nothing since
        :class:`~pymongo.replica_set_connection.ReplicaSetConnection` does not
        have (or need) an :meth:`end_request` method.
        """
        pass

