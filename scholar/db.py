import sqlite3

import click


def get_db():
    db = sqlite3.connect(
        "../instance/paper.sqlite",
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row

    return db


def close_db(e=None):
    db = pop('db', None)

    if db is not None:
        db.close()
