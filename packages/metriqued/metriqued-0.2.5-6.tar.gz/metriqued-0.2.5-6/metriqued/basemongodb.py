#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward" <cward@redhat.com>

import logging
import os
try:
    from pymongo import MongoClient
    mongo_client_support = True
except ImportError:
    from pymongo import Connection
    mongo_client_support = False
from pymongo.errors import ConnectionFailure


class BaseMongoDB(object):
    def __init__(self, db, host, user=None, password=None, auth=False,
                 port=None, ssl=None, ssl_keyfile=None, tz_aware=True,
                 ssl_certfile=None, write_concern=1, journal=False,
                 fsync=False):

        pid = os.getpid()
        self.logger = logging.getLogger('metriqued.%i.mongodb' % pid)

        if ssl_keyfile:
            ssl_keyfile = os.path.expanduser(ssl_keyfile)
        if ssl_certfile:
            ssl_certfile = os.path.expanduser(ssl_certfile)

        self.auth = auth
        self.host = host
        self.user = user
        self.password = password
        self._db = db

        self.ssl = ssl
        self.ssl_keyfile = ssl_keyfile
        self.ssl_certfile = ssl_certfile
        self.port = port
        self.write_concern = write_concern
        self.fsync = fsync
        self.journal = journal
        self.tz_aware = tz_aware

    def _auth_db(self):
        '''
        by default the default user only has read-only access to db
        '''
        self.logger.debug('MongoDB Authentication: %s' % self.user)
        if not self.auth:
            pass
        elif not self.password:
            raise ValueError("no mongo authentication password provided")
        else:
            admin_db = self._proxy['admin']
            if not admin_db.authenticate(self.user, self.password):
                raise RuntimeError(
                    "MongoDB failed to authenticate user (%s)" % self.user)
        return self._proxy[self._db]

    def close(self):
        if hasattr(self, '_proxy'):
            self._proxy.close()

    @property
    def db(self):
        retries = 3
        # return the connected, authenticated database object
        while retries:
            try:
                return self._load_db_proxy()
            except ConnectionFailure as e:
                self.logger.warn("[%i] MongoDB Failed to connect (%s): %s" % (
                            retries, self.host, e))
                retries -= 1
                self._db_proxy = None
        else:
            raise ConnectionFailure(
                "MongoDB Failed to connect (%s): %s" % (self.host, e))

    def __getitem__(self, collection):
        return self.db[collection]

    def _load_mongo_client(self, **kwargs):
        self._proxy = MongoClient(self.host, self.port,
                                  tz_aware=self.tz_aware,
                                  w=self.write_concern,
                                  j=self.journal,
                                  fsync=self.fsync,
                                  **kwargs)

    def _load_mongo_connection(self, **kwargs):
            self._proxy = Connection(self.host, self.port,
                                     tz_aware=self.tz_aware,
                                     w=self.write_concern,
                                     j=self.journal,
                                     fsync=self.fsync,
                                     **kwargs)

    def _load_db_proxy(self):
        if not (hasattr(self, '_db_proxy') and self._db_proxy):
            self.logger.debug('Loading NEW Mongodb Proxy connection')
            kwargs = {}
            if self.ssl:
                if self.ssl_keyfile:
                    # include ssl keyfile only if its defined
                    # otherwise, certfile must be crt+key pem combined
                    kwargs.update({'ssl_keyfile': self.ssl_keyfile})

                # include ssl options only if it's enabled
                kwargs.update(dict(ssl=self.ssl,
                                   ssl_certfile=self.ssl_certfile))
            if mongo_client_support:
                self._load_mongo_client(**kwargs)
            else:
                self._load_mongo_connection(**kwargs)
            self._db_proxy = self._auth_db()
        return self._db_proxy

    def set_collection(self, collection):
        self.collection = collection
