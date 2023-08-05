RDS-HOST
========

A simple command line utility, allowing you to find the hostname associated with
your Amazon RDS instance name.

Also has a simple wrapper for PostgreSQL's psql utility. If you want a similar
script for MySQL or Oracle, patches are welcome.

A few examples::

    # w/o arg: prints all active instances
    % rds-host
    mydbinstance    mydbinstance.c6ulnjwxjm.us-west-2.rds.amazonaws.com:5432
    myotherdbinstance  myotherdbinstance.d5ulnswdjyf.us-west-2.rds.amazonaws.com:5432

    # w/ arg: prints host name of matching instance
    % rds-host mydbinstance
    mydbinstance.c6ulnjwxjm.us-west-2.rds.amazonaws.com:5432

    # connect to the instance with psql
    % rds-psql mydbinstance -U mydbuser mydbname
    Connecting to mydbinstance.c6ulnjwxjm.us-west-2.rds.amazonaws.com...
    Password for user mydbuser:
    psql (9.0.5, server 9.3.1)
    WARNING: psql version 9.0, server version 9.3.
    Some psql features might not work.
    SSL connection (cipher: DHE-RSA-AES256-SHA, bits: 256)
    Type "help" for help.

    mydbname=>



