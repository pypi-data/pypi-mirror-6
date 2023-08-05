"""Efficiently load large quantities of data into database"""

import time
import cStringIO
import csv
from log import getLogger

class DbBulkInsert(object):
    """Wrapper around psycopg's copy_expert() to insert data in bulk.

    Usage 1 (recommended):

    # no need to call flush()
    with DbBulkInsert(db, ...) as bic:
        # one or more of these...
        bic.update(...)

    Usage 2:

    bic = DbBulkInsert(db, ...)
    # one or more of these...
    bic.update(...)
    # user *has* to call this
    bic.flush()

    Since destructor execution in Python is unreliable
    (http://stackoverflow.com/questions/1481488/how-to-call-the-del-method),
    user has to manually call flush(). With a context manager,
    the flush() is called automatically.
    """

    def __init__(self, db, table_name, column_names, cache_size=100000):
        """Initialize the cache.

        table_name [string]:
            name of the destination table. It is expected that this table already exists.

        column_names [list of strings]:
            a list of strings, representing columns in the table that need to be populated;
            order matters here, since its assumed that each incoming row of data matches
            these column names; it is assumed that these columns already exist in the above table.

        cache_size [integer]:
            how many rows of input should be buffered before writing to the db using copy_from?
            obvious tradeoffs for values of this argument:
            too large => you risk running out of physical memory
            too small => you make too many calls to copy_from() and lose efficiency in bulk.
        """

        self.__delimiter = '|'
        self.db = db
        self.table = table_name
        self.column_names = column_names
        self.cache_size = cache_size
        self._reset()
        self.logger = getLogger()

    def _reset(self):
        self.fd = cStringIO.StringIO()
        self.c = csv.writer(self.fd, delimiter=self.__delimiter)
        self.lines = 0

    def update(self, new_row):
        self.c.writerow(new_row)
        self.lines += 1
        if self.lines >= self.cache_size:
            self.flush()

    def flush(self):
        self.fd.seek(0)
        cursor = self.db.cursor()
        # XXX quote column names for better safety
        columns_sql = ', '.join(self.column_names)
        copy_sql = "COPY %s (%s) FROM stdin WITH csv DELIMITER '%s'" % (self.table,
                                                                        columns_sql,
                                                                        self.__delimiter)
        start_time = time.time()
        cursor.copy_expert(copy_sql, self.fd)
        self.logger.debug("inserted %d rows into db table '%s' [%.2fs]" % (self.lines,
                                                                           self.table,
                                                                           time.time() - start_time))
        cursor.close()
        self.fd.close()
        self._reset()

    # for use with contextlib
    def close(self):
        return self.flush()

    def __enter__(self):
        return self

    def __exit__(self, exec_type, exec_value, exec_tb):
        if not exec_tb:
            self.flush()
