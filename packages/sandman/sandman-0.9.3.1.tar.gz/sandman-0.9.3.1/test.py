from sandman import app as application
from sandman.model import activate
import logging
import os, sys
 
root = logging.getLogger()
ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.WARNING)
root.addHandler(ch)
 
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite+pysqlite:///test.sqlite3'
@application.route("/")
def hello():
    return "Hello World!"
 
if __name__ == "__main__":
    activate(browser=False, admin=True)
    application.debug = True
    application.run(host='0.0.0.0', port=9090)
