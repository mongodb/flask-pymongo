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


from pymongo import *

class PyMongo(object):
    """TODO.
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

        self.app.after_request(self._after_request)

    def connect(self):
        """Sub-classes may override this to return a specific type
        of connection, or to modify the connection in some way.
        """
        return Connection(
            host=self.host,
            port=self.port,
        )

    def _after_request(self, response):
        """:meth:`~flask.Flask.after_request` handler which calls
        :meth:`~pymongo.connection.Connection.end_request`.
        """
        self.cx.end_request()
        return response

    def __getattr__(self, name):
        """Proxy unknown attribute access directly to the
        :class:`~pymongo.database.Database`. This lets you access
        collections directly as attributes of the :class:`PyMongo`
        object.
        """
        return getattr(self.db, name)

def monkey_patch():
    """Adds Flask-PyMongo extension methods to PyMongo classes:

     - :meth:`_find_one_or_404`: like
       :meth:`~pymongo.collection.Collection.find_one`, but
       raises a 404 Not Found exception if no document is found.
    """
    import flask
    import pymongo.collection

    def _find_one_or_404(self, *args, **kwargs):
        found = self.find_one(*args, **kwargs)
        if not found:
            flask.abort(404)
        return found

    pymongo.collection.Collection.find_one_or_404 = _find_one_or_404

monkey_patch()
del monkey_patch

