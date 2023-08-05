km2pg
-----

Load raw kissmetrics data from specified s3 bucket into specified postgres database.

To install
----------

In this directory, run the following command:

    python setup.py install

To use
------

Once installed, a new script, named km2pg should now be available in PATH, which can be used as follows:

    km2pg \
         -b name_of_s3_bucket \
         -m postgres_hostname \
         -p postgres_port \
         -d postgres_dbname \
         -u postgres_username \
         -w postgres_passwd \
         -a aws_access_key \
         -s aws_secret_key

For more details, see km2pg --help.

Requires
--------

   * boto: Python library for AWS
   * psycopg: postgres Python client library

Comment
-------

This script can safely be run from an Amazon spot instance, where checkpointing is important, since the script can be interrupted at any moment.

Strategy
--------

kissmetrics deposits raw data into multiple json files:

    bucket/
        revisions/
            1.json
            2.json
            ...
            N.json

kissmetrics provides an 'index' file at:

    bucket/index.csv

This index file lists all the json files that kissmetrics has currently deposited in the 'revisions' folder above.

Our strategy is to process the json files in the order they appear in index.csv (which happens to be in order of increasing time).

In our postgres instance, we will maintain our progress through index.csv. This approach assumes that kissmetrics only ever appends to index.csv, and never edits.
