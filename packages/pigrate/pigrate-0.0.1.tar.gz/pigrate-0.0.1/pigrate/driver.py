# coding: utf-8

import re
from pigrate import internal


def _shrink(text):
    return re.sub(r'\s+', ' ', text).strip()


def _split_sql(sql, delimiter=';'):
    sql = unicode(sql)
    result = []

    def append_statement(statement):
        statement = _shrink(statement)
        if statement:
            result.append(statement)

    is_in_single_string = False
    is_in_double_string = False

    begin_pos = 0
    i = 0
    while i < len(sql):
        if sql[i] == "\\":
            i += 1
        if sql[i].startswith('""') and is_in_double_string:
            i += 1
        if sql[i].startswith("''") and is_in_single_string:
            i += 1
        if sql[i] == "'" and not is_in_double_string:
            is_in_single_string = not is_in_single_string
        if sql[i] == '"' and not is_in_single_string:
            is_in_double_string = not is_in_double_string
        if not is_in_double_string and not is_in_single_string and sql[i:].startswith(delimiter):
            append_statement(sql[begin_pos:i])
            begin_pos = i + len(delimiter)
        i += 1
    append_statement(sql[begin_pos:])

    return result


def dbapi(_driver, *args, **kwargs):
    OperationalError = getattr(_driver, 'OperationalError')

    def execute_script(cur, script, delimiter=';'):
        statements = _split_sql(script, delimiter=delimiter)
        for statement in statements:
            cur.execute(statement)

    class connect(object):
        def __init__(self):
            pass
        def __enter__(self):
            self.conn = _driver.connect(*args, **kwargs)
            return self.conn
        def __exit__(self, exc_type, exc_value, tb):
            self.conn.close()

    def driver(mig, undo=False):
        delimiter = mig.script.delimiter if hasattr(mig.script, 'delimiter') else ';'
        with connect() as conn:
            cur = conn.cursor()
            if not undo:
                execute_script(cur, mig.script.up, delimiter=delimiter)
                cur.execute(_shrink("""
                    INSERT INTO _pig_status (id, applied_at) VALUES (?, ?);
                """), (mig.id, internal.util.current_utc_millis()))
            else:
                execute_script(cur, mig.script.down, delimiter=delimiter)
                cur.execute(_shrink("""
                    DELETE FROM _pig_status WHERE id = ?;
                """), (mig.id, ))
            conn.commit()

    def status():
        result = []
        with connect() as conn:
            try:
                cur = conn.cursor()
                cur.execute('SELECT id, applied_at FROM _pig_status ORDER BY id')
                for row in cur.fetchall():
                    id = int(row[0])
                    applied_at = int(row[1])
                    result.append(internal.PigrationStatus(id, applied_at))
            except OperationalError as e:
                return None # the table does not exist
        return result

    def pigratize():
        with connect() as conn:
            conn.cursor().execute(_shrink("""
                CREATE TABLE _pig_status (
                    id INTEGER NOT NULL PRIMARY KEY,
                    applied_at INTEGER NOT NULL
                );
            """))
            conn.commit()

    def unpigratize():
        with connect() as conn:
            conn.cursor().execute(_shrink("""
                DROP TABLE _pig_status;
            """))
            conn.commit()

    driver.status = status
    driver.pigratize = pigratize
    driver.unpigratize = unpigratize
    return driver


def mysql(host, db, port=3306, user=None, passwd=None):
    import MySQLdb as _driver
    return dbapi(_driver, host=host, user=user, passwd=passwd, db=db, port=port)


def sqlite3(db):
    import sqlite3 as _driver
    return dbapi(_driver, db)

