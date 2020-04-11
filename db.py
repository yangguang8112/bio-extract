import sqlite3
import os

WORK_DIR = os.getcwd()
script_dir = os.path.abspath(os.path.dirname(__file__))

def get_db():
    db_file = os.path.join(WORK_DIR, 'paper.sqlite')
    db = sqlite3.connect(
            db_file,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    db.row_factory = sqlite3.Row

    return db


def close_db(e=None):
    db = pop('db', None)

    if db is not None:
        db.close()

def init_db():
    sql_file = os.path.join(script_dir, 'schema.sql')
    db = get_db()

    with open(sql_file,'r') as f:
        db.executescript(f.read())#.decode('utf8'))

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'init':
        init_db()
