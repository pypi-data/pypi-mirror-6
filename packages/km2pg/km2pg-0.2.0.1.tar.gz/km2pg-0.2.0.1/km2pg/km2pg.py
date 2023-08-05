"""
Load kissmetrics raw data from specified s3 bucket into specified postgres database.

Requires:
   * boto: Python library for AWS
   * psycopg: postgres Python client library

Comment:

This script can safely be run from an Amazon spot instance,
where checkpointing is important, since the script
can be interrupted at any moment.

Strategy:

kissmetrics deposits raw data into multiple json files:

    bucket/
        revisions/
            1.json
            2.json
            ...
            N.json

kissmetrics provides an 'index' file at:
    bucket/index.csv

This index file lists all the json files that kissmetrics
has currently deposited in the 'revisions' folder above.

Our strategy is to process the json files in the order
they appear in index.csv (which happens to be in order of
increasing time).

In our postgres instance, we will maintain our progress through
index.csv. This approach assumes that kissmetrics only ever
appends to index.csv, and never edits.
"""

import os
import csv
import json
try:
    import cStringIO as StringIO
except:
    import StringIO
from datetime import datetime

from boto.s3.connection import S3Connection
from pginsert import DbBulkInsert
import pgdb
from log import getLogger

DEFAULT_INDEX_FILENAME = 'index.csv'

logger = getLogger()

class km2pgError(Exception):
    pass

def mkfile(bucket, keyname):
    f = StringIO.StringIO()
    key = bucket.get_key(keyname)
    key.get_contents_to_file(f)
    f.seek(0)
    return f

def gets3conn(aws_access_key, aws_secret_key):
    if aws_access_key and aws_secret_key:
        return S3Connection(aws_access_key, aws_secret_key)
    else:
        # look for env variables: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
        return S3Connection()

def get_current_progress(db, progress_table):
    """How many lines in index.csv have we processed?

    progcoll -> name of the postgres table that maintains processing info.

    This table contains exactly one row, with one integer value,
    that represents the number of input lines processed.

    If starting afresh, the value will be 0.
    """

    sql = """
    SELECT progress
      FROM %(progress_table)s
    """ % locals()
    return db.execute(sql).fetchone()[0]

def update_progress(db, progress_table, newlinenum):
    sql = """
    UPDATE %(progress_table)s
       SET
        progress = %%(newlinenum)s
    """ % locals()
    db.executemany(sql, locals())

def get_new_data(bucket, indexfilename, current_progress):
    """Returns new json files that need to be processed.

    Return value is a list of tuples of the form:

    (linenum, jsonfile).

    The caller is responsible for updating progress
    upon successful handling of each json file.
    This is where linenum comes in handy.
    """
    f = mkfile(bucket, indexfilename)
    found = processed = 0
    reader = csv.reader(f, delimiter=',')
    for n, line in enumerate(reader, 0):
        # first line is header line: will also be skipped
        found += 1
        if n <= current_progress:
            continue
        jsonfile = line[0]  # first column is the json file location
        yield (n, jsonfile)
        processed += 1
    f.close()
    if not found:
        raise km2pgError("kissmetrics index file is empty")
    if not processed:
        logger.info("no new data to process!")
    else:
        logger.info("found %(processed)d new files" % locals())

def _jsonload(f):
    for linenum, line in enumerate(f, 1):
        try:
            yield (linenum, json.loads(line))
        except:
            logger.error("unable to parse json data from line num %(linenum)s: %(line)s" % locals())

__cardinals = frozenset(['_p', '_p2', '_t', '_n'])
def get_row_data(fp):
    """Converts each km json dict into one or more tuples of the form:

    (person, time, event, alias, key, value)

    This can be bulk-loaded into the database using the COPY command.
    """

    for linenum, doc in _jsonload(fp):
        person, event_time = doc['_p'], doc['_t']
        event_time = datetime.utcfromtimestamp(event_time)
        alias = doc.get('_p2')
        event_name = doc.get('_n')
        remaining_data = dict((k, v) for k, v in doc.items() if k not in __cardinals)
        if remaining_data:
            for k, v in remaining_data.items():
                yield (linenum, person, event_time, event_name, alias, k, v)
        else:
            yield (linenum, person, event_time, event_name, alias, None, None)

def sql_for_temp_creation(tablename):
    return """
    CREATE TEMP TABLE %(tablename)s (
        --- I. columns from the kissmetrics feed
        linenum      INTEGER,
        p            TEXT,     -- person
        p2           TEXT,     -- alias
        n            TEXT,     -- action
        t            TIMESTAMP WITHOUT TIME ZONE,
        k            TEXT,
        v            TEXT,
        --- II. derived columns
        userid       INTEGER,
        aliasid      INTEGER,
        actionid     INTEGER,
        eventid      INTEGER,
        keyid        INTEGER,
        new_p        BOOLEAN NOT NULL DEFAULT false,
        new_p2       BOOLEAN NOT NULL DEFAULT false,
        new_n        BOOLEAN NOT NULL DEFAULT false,
        new_e        BOOLEAN NOT NULL DEFAULT false,
        new_k        BOOLEAN NOT NULL DEFAULT false );
    """ % locals()

def sql_for_users(tablename):
    return """
    --- 1. identify new users
    UPDATE %(tablename)s t
       SET
        new_p = true,
        new_e = true         -- if new person, then also new event
     WHERE NOT EXISTS (
         SELECT 1 FROM users u
          WHERE u.name = t.p );

    INSERT INTO users (name)
    SELECT DISTINCT p
      FROM %(tablename)s
     WHERE new_p;

    UPDATE %(tablename)s t
       SET userid = u.userid
      FROM users u
     WHERE t.p = u.name;

    --- 2. identify new aliases
    UPDATE %(tablename)s t
       SET new_p2 = true
     WHERE p2 NOTNULL
       AND NOT EXISTS (
         SELECT 1 FROM users u
          WHERE u.name = t.p2 );

    INSERT INTO users (name)
    SELECT DISTINCT p2
      FROM %(tablename)s
     WHERE new_p2;

    UPDATE %(tablename)s t
       SET aliasid = u.userid
      FROM users u
     WHERE t.p2 = u.name;

    --- 3. record any new associations
    INSERT INTO aliases (userid, aliasid, since)
    WITH ranked_aliases AS (
        SELECT userid, aliasid, t, rank() OVER w
          FROM %(tablename)s m
         WHERE p2 NOTNULL
        WINDOW w AS (PARTITION BY userid, aliasid ORDER BY linenum) )
    SELECT userid, aliasid, t
      FROM ranked_aliases m
     WHERE m.rank = 1
       AND NOT EXISTS (
        SELECT 1 FROM aliases a
         WHERE (a.userid, a.aliasid) = (m.userid, m.aliasid) );
    """ % locals()

def sql_for_actions(tablename):
    return """
    UPDATE %(tablename)s t
       SET new_n = true
     WHERE n NOTNULL
       AND NOT EXISTS (
         SELECT 1 FROM actions a
          WHERE a.name = t.n );

    INSERT INTO actions (name)
    SELECT DISTINCT n
      FROM %(tablename)s
     WHERE new_n;

    UPDATE %(tablename)s t
       SET actionid = a.actionid
      FROM actions a
     WHERE t.n = a.name;
    """ % locals()

def sql_for_keys(tablename):
    return """
    UPDATE %(tablename)s m
       SET new_k = true
     WHERE k NOTNULL
       AND NOT EXISTS (
         SELECT 1 FROM keys k
          WHERE k.name = m.k );

    INSERT INTO keys (name)
    SELECT DISTINCT k
      FROM %(tablename)s
     WHERE new_k;

    UPDATE %(tablename)s m
       SET keyid = k.keyid
      FROM keys k
     WHERE m.k = k.name;
    """ % locals()

def sql_for_events(tablename):
    return """
    UPDATE %(tablename)s m
       SET new_e = true
     WHERE NOT new_e
       AND NOT EXISTS (
         SELECT 1 FROM events k
          WHERE (k.userid, k.t) = (m.userid, m.t) );

    INSERT INTO events (userid, t)
    SELECT DISTINCT userid, t
      FROM %(tablename)s
     WHERE new_e;

    UPDATE %(tablename)s m
       SET eventid = e.eventid
      FROM events e
     WHERE (m.userid, m.t) = (e.userid, e.t);
    """ % locals()

def sql_for_duplicates(tablename):
    return """
    WITH exclude_dups_by_event_name AS (    -- because of the DESC in the ORDER BY,
        SELECT                              -- we will prefer later updates
            eventid, actionid, linenum,
            rank() OVER (PARTITION BY eventid, actionid
                         ORDER BY linenum DESC)
          FROM %(tablename)s
         WHERE actionid NOTNULL )
    DELETE FROM %(tablename)s t1
     USING exclude_dups_by_event_name t2
     WHERE
        (t1.eventid, t1.actionid, t1.linenum) = (t2.eventid, t2.actionid, t2.linenum)
       AND t2.rank > 1;                     -- XXX too eager?

    WITH exclude_dups_by_event_property AS (
        SELECT
            eventid, keyid, linenum,
            rank() OVER (PARTITION BY eventid, keyid
                         ORDER BY linenum DESC)
          FROM %(tablename)s
         WHERE keyid NOTNULL )
    DELETE FROM %(tablename)s t1
     USING exclude_dups_by_event_property t2
     WHERE
        (t1.eventid, t1.keyid, t1.linenum) = (t2.eventid, t2.keyid, t2.linenum)
       AND t2.rank > 1;

    DELETE FROM %(tablename)s t               -- there can only be one event with a given name
     WHERE EXISTS (                           -- for a given (person, timestamp) combo.
        SELECT 1 FROM event_actions m
         WHERE (m.eventid, m.actionid) = (t.eventid, t.actionid) );

    DELETE FROM %(tablename)s t               -- there can only be one key with a given name
     WHERE EXISTS (                           -- for a given (person, timestamp) combo
        SELECT 1 FROM event_properties m
         WHERE (m.eventid, m.keyid) = (t.eventid, t.keyid) );
    """ % locals()

def sql_for_remainder(tablename):
    return """
    INSERT INTO event_actions (eventid, actionid)
    SELECT DISTINCT eventid, actionid
      FROM %(tablename)s
     WHERE eventid NOTNULL
       AND actionid NOTNULL;

    INSERT INTO event_properties (eventid, actionid, keyid, value)
    SELECT eventid, actionid, keyid, v
      FROM %(tablename)s;
    """ % locals()

def json2db(db, bucket, linenum, jsonfile):
    f = mkfile(bucket, jsonfile)
    column_names = ('linenum', 'p', 't', 'n', 'p2', 'k', 'v')       # order matters here
    with DbBulkInsert(db, 'tmp_new_activity', column_names) as bic:
        for row in get_row_data(f):
            bic.update(row)
    f.close()
    # --- I. associate keys with all concepts
    sql = sql_for_users('tmp_new_activity')
    db.executemany(sql)
    sql = sql_for_actions('tmp_new_activity')
    db.executemany(sql)
    sql = sql_for_keys('tmp_new_activity')
    db.executemany(sql)
    sql = sql_for_events('tmp_new_activity')
    db.executemany(sql)
    # --- II. fix any duplicates
    sql = sql_for_duplicates('tmp_new_activity')
    db.executemany(sql)
    # --- III. insert remaining data
    sql = sql_for_remainder('tmp_new_activity')
    db.executemany(sql)

def mkdsn(host, port, user, password, dbname):
    return "dbname=%(dbname)s user=%(user)s host=%(host)s port=%(port)s password=%(password)s" % locals()

def km2pg(s3bucketname,
          host, port, dbname, user, passwd,
          indexfilename=DEFAULT_INDEX_FILENAME,
          aws_access_key=None, aws_secret_key=None):
    progress_table = 'parse_progress'
    # --- 1. set up postgres connection
    db = pgdb.DB(mkdsn(host, port, user, passwd, dbname))
    # --- 2. set up connection to aws
    s3conn = gets3conn(aws_access_key, aws_secret_key)
    bucket = s3conn.get_bucket(s3bucketname)
    # --- 3. actual work
    db.executemany(sql_for_temp_creation('tmp_new_activity'))
    p = get_current_progress(db, progress_table)
    logger.debug("current progress: %(p)s" % locals())
    for linenum, jsonfile in get_new_data(bucket, indexfilename, p):
        logger.debug("processing line %(linenum)s from file %(indexfilename)s: %(jsonfile)s ..." % locals())
        db.execute("BEGIN;")
        json2db(db, bucket, linenum, jsonfile)
        update_progress(db, progress_table, linenum)
        db.execute("COMMIT;")
        db.executemany("TRUNCATE tmp_new_activity;")
    db.executemany("DROP TABLE tmp_new_activity;")
