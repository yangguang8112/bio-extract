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
