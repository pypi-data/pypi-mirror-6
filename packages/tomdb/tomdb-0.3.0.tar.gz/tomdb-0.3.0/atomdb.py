from __future__ import absolute_import, division, with_statement

import logging
import time
import pymysql

version = "0.0.1"
version_info = (0, 0, 1, 0)

class Connection(object):

    def __init__(self, host, database, user=None, password=None, auto_commit=True,
                 use_charset='utf8',max_idle_time=7 * 3600, connect_timeout=None,
                 time_zone="+8:00", use_unicode=True, port=3306):
        self.host = host
        self.database = database
        self.max_idle_time = float(max_idle_time)

        args = dict(host=host,use_unicode=use_unicode, charset=use_charset, user=user,
                    database=database, init_command=('SET time_zone = "%s"' % time_zone),
                    connect_timeout=connect_timeout, sql_mode="TRADITIONAL",passwd=password,
                    autocommit=auto_commit, port=port,)

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception:
            logging.error("Cannot connect to MySQL on %s", self.host,
                          exc_info=True)

    def __del__(self):
        self.close()

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def commit(self):
        """Commit"""
        self._db.commit()

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = pymysql.connect(**self._db_args)
        #print self._db_args

    def iter(self, query, *parameters, **kwparameters):
        """Returns an iterator for the given query and parameters."""
        self._ensure_connected()
        cursor = pymysql.cursors.SSCursor(self._db)
        try:
            self._execute(cursor, query, parameters, kwparameters)
            column_names = [d[0] for d in cursor.description]
            for row in cursor:
                yield dict(zip(column_names, row))
        finally:
            cursor.close()

    def query(self, query, *parameters, **kwparameters):
        """Returns a row list for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            column_names = [d[0] for d in cursor.description]
            return [dict(zip(column_names, row)) for row in cursor]
        finally:
            cursor.close()

    def onelist(self, query, *parameters, **kwparameters):
        """Returns one column of the list for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            return [row[0] for row in cursor]
        finally:
            cursor.close()

    def oneset(self, query, *parameters, **kwparameters):
        """Returns one column of the set for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            return {row[0] for row in cursor}
        finally:
            cursor.close()

    def one(self, query, *parameters, **kwparameters):
        """Returns one str for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            rows = [row[0] for row in cursor]
        finally:
            cursor.close()
        if len(rows) == 1:
            return rows[0]
        else:
            raise Exception("Multiple rows returned for Database.one() query")

    # rowcount is a more reasonable default return value than lastrowid,
    # but for historical compatibility execute() must return lastrowid.
    def execute(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query."""
        return self.execute_lastrowid(query, *parameters, **kwparameters)

    def execute_lastrowid(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def execute_rowcount(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the rowcount from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            return cursor.rowcount
        finally:
            cursor.close()

    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def _execute(self, cursor, query, parameters, kwparameters):
        try:
            return cursor.execute(query, kwparameters or parameters)
        except OperationalError:
            logging.error("Error connecting to MySQL on %s", self.host)
            self.close()
            raise

    def _ensure_connected(self):
        if (self._db is None or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()
