"""Run server"""
from sandman import app, db
import os
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite+pysqlite:////Users/jknupp/code/github_code/sandman/sandman/test/data/chinook'
app.secret_key = 's3cr3t'
import models
app.run(host='0.0.0.0', debug=True)
