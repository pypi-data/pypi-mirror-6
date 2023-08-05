"""\
A (deliberately) thin wrapper around psycopg2.
"""

import sys
import time
import os

import sqlparse
import psycopg2, psycopg2.extensions, psycopg2.extras

from log import getLogger

DEFAULT_CURSOR_FACTORY = psycopg2.extras.NamedTupleCursor

def _logquery(query):
    logger = getLogger()
    logger.info("SQL Query ->")
    logger.info(query)

def _logresult(cursor, duration):
    logger = getLogger()
    logger.info( "Status: %s, duration: %.3f seconds" % (cursor.statusmessage, duration) )

def _appname():
    return os.path.splitext(os.path.basename(sys.argv[0]))[0]

class DB(object):
    """Wrapper around connection+cursor object."""

    def __init__(self,
                 dsn=None,
                 database=None, user=None, password=None, host=None, port=None,
                 cursor_factory=None, async=False, **kwargs):
        """Supports same arguments as psycopg2.connect.

        See http://initd.org/psycopg/docs/module.html#psycopg2.connect
        """

        self.logger = getLogger()
        fapp = _appname()
        if dsn:
            dsn += " fallback_application_name=%(fapp)s" % locals()
        else:
            kwargs['fallback_application_name'] = fapp
        self.conn = psycopg2.connect(dsn=dsn,
                                     database=database, user=user, password=password, host=host, port=port,
                                     cursor_factory=cursor_factory, async=async, **kwargs)
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.logger.info("Connected to %s" % (self,))

    def __str__(self):
        return "DB(%s)" % (self.conn.dsn,)

    def cursor(self, cursor_factory=DEFAULT_CURSOR_FACTORY):
        """Get a new psycopg cursor."""
        return self.conn.cursor(cursor_factory=cursor_factory)

    def execute(self, query, params=None, cursor_factory=DEFAULT_CURSOR_FACTORY):
        """Run query in a new cursor and return the cursor."""

        cursor = self.cursor(cursor_factory=cursor_factory)
        _logquery(cursor.mogrify(query, params))
        start_time = time.time()
        cursor.execute(query, params)
        _logresult(cursor, time.time() - start_time)
        return cursor

    def executemany(self, script, params=None, cursor_factory=DEFAULT_CURSOR_FACTORY):
        """Run a string or stream of SQL statements. Returns [cursors]."""
        queries = sqlparse.split(script)
        if not params:
            params = None
        return [self.execute(q, params=params, cursor_factory=cursor_factory)
                for q in queries if q.strip()]

    def close(self):
        if self.conn:
            self.conn.close()
            del self.conn
        else:
            self.logger.info("Connection already closed to %s" % (self,))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
