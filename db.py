import sqlite3

def get_db():
    db = sqlite3.connect(
            "./instance/paper.sqlite",
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    db.row_factory = sqlite3.Row

    return db


def close_db(e=None):
    db = pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with open('schema.sql','r') as f:
        db.executescript(f.read())#.decode('utf8'))

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'init':
        init_db()
