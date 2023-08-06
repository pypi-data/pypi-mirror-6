"""Main test class for sandman"""

import os
import shutil
import json
import datetime

from flask import Flask

from sandman import db
from test_sandman import TestSandmanBase

class TestExistingModel(TestSandmanBase):
    """Base class for all sandman test classes."""

    DB_LOCATION = os.path.join(os.getcwd(), 'tests', 'existing.sqlite3')

    def setup_method(self, _):
        """Grab the database file from the *data* directory and configure the
        app."""
        shutil.copy(
                os.path.join(
                    os.getcwd(),
                    'tests',
                    'data',
                    'existing.sqlite3'),
                self.DB_LOCATION)

        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + self.DB_LOCATION
        app.config['SANDMAN_SHOW_PKS'] = False
        app.config['SANDMAN_GENERATE_PKS'] = False
        app.config['TESTING'] = True
        db.init_app(app)
        self.app = app.test_client()
        #pylint: disable=unused-variable
        from . import existing_models

    def teardown_method(self, _):
        """Remove the database file copied during setup."""
        os.unlink(self.DB_LOCATION)
        #pylint: disable=attribute-defined-outside-init
        self.app = None


    def test_use_existing(self):
        """Can we successfully view the admin page for a pre-defined declarative
        class?"""
        self.get_response('/admin/somemodelview/', 200)
