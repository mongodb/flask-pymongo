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

__all__ = ('PyMongo', 'ASCENDING', 'DESCENDING')


from flask import abort, request
from pymongo import Connection, ASCENDING, DESCENDING
from pymongo.collection import Collection

from flask_pymongo.util import monkey_patch


class PyMongo(object):
    """Automatically connects to MongoDB using parameters defined in Flask
    configuration named ``MONGO_HOST``, ``MONGO_PORT``, and ``MONGO_DBNAME``
    (assuming default `config_prefix` of "MONGO").

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

        self.host = app.config.get('%s_HOST' % config_prefix, 'localhost')
        self.port = app.config.get('%s_PORT' % config_prefix, 27017)
        dbname = app.config.get('%s_DBNAME' % config_prefix)
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

