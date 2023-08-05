"""Script to run sandman via command line

Usage:
    sandmanctl.py URI [--primary-keys --all-columns-primary]

Start sandman and connect to database at URI

Supported database dialects:

[PostgreSQL]
[MySQL]
[Oracle]
[Microsoft SQL Server]
[SQLite]
[Drizzle]
[Firebird]
[Sybase]

External dialects and packages:

[IBM DB2]: ibm_db_sa
[SAP Sybase SQL Anywhere]: sqlalchemy-sqlany
[MonetDB]: sqlalchemy-monetdb

Arguments:
    URI     RFC-1738 style database URI

Options:
    -h --help                   Show this screen.
    -p --primary-keys           Display primary key columns in the admin
                                interface
    -a --all-columns-primary    Use the combination of all columns as the
                                primary key for tables without primary keys
                                (primary keys are required by the mapping
                                engine). Implies --primary-keys

'postgresql+psycopg2://scott:tiger@localhost/test'
'postgresql+psycopg2://scott:tiger@localhost/test' --all-columns-primary

"""
from __future__ import absolute_import

from docopt import docopt

from sandman import app
from sandman.model import activate

def main(test_options=None):
    """Main entry point for script."""
    options = test_options or docopt(__doc__)
    app.config['SQLALCHEMY_DATABASE_URI'] = options['URI']
    if '--all-columns-primary' in options:
        app.config['SANDMAN_ALL_PRIMARY'] = True
        app.config['SANDMAN_SHOW_PKS'] = True
    else:
        app.config['SANDMAN_ALL_PRIMARY'] = False
        app.config['SANDMAN_SHOW_PKS'] = '--primary-keys' in options
    activate(name='sandmanctl')
    app.run('0.0.0.0', debug=True)
