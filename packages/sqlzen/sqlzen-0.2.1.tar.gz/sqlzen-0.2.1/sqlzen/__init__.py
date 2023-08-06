import sqlalchemy.exc
from sqlalchemy.orm import sessionmaker

from functions import first, keys, last, merge, rest


INSERT_TEMPLATES = {
    'psycopg2': 'INSERT INTO {0} ({1}) VALUES ({2}) RETURNING *',
    'pymysql': 'INSERT INTO {0} ({1}) VALUES ({2})'}


UPDATE_TEMPLATES = {
    'psycopg2': 'UPDATE {0} SET {1} {2} RETURNING *',
    'pymysql': 'UPDATE {0} SET {1} {2}'}


def get_session(engine):
    """Return a session to a database"""
    return sessionmaker(bind=engine)()


def query(db, sql_and_params, as_arrays=False):
    """Perform a database query"""
    result_proxy = db.connection().execute(*sql_and_params)
    cols, rows = result_proxy.keys(), result_proxy.fetchall()
    if as_arrays:
        return tuple(zip(*rows))
    return tuple(dict(zip(cols, row)) for row in rows)


def execute(db, sql_and_params):
    """Perform a general (non-select) SQL operation"""
    result_proxy = db.connection().execute(*sql_and_params)
    row_count = result_proxy.rowcount
    try:
        cols, rows = result_proxy.keys(), result_proxy.fetchall()
        return tuple(dict(zip(cols, row)) for row in rows)
    except sqlalchemy.exc.ResourceClosedError:
        return row_count


def insert(db, table, row_map):
    """Perform an insert"""
    sql = INSERT_TEMPLATES[db.get_bind().driver].format(
        table,
        ", ".join(tuple(k for k in row_map)),
        ", ".join(tuple("%(" + k + ")s" for k in row_map)))
    return execute(db, (sql, row_map))


def update(db, table, set_map, where_clause):
    """Perform an update"""
    def where(sql_and_params):
        if not rest(sql_and_params):
            return sql_and_params
        parts = first(sql_and_params).split('%s')
        sql = ()
        for i, chars in enumerate(rest(parts)):
            sql += ('%(_{0})s{1}'.format(i, chars),)
        params = ()
        for i, value in enumerate(rest(sql_and_params)):
            params += (('_{0}'.format(i), value),)
        return (first(parts) + ''.join(sql), dict(params))
    where_sql_and_params = where(where_clause)
    sql = UPDATE_TEMPLATES[db.get_bind().driver].format(
        table,
        ", ".join([k + "=%(" + k + ")s" for k in set_map]),
        first(where_sql_and_params))
    if rest(where_sql_and_params):
        params = merge(set_map, last(where_sql_and_params))
    else:
        params = set_map
    return execute(db, (sql, params))


def delete(db, table, where_clause):
    """Perform a delete"""
    sql = "DELETE FROM {0} {1}".format(table, first(where_clause))
    return execute(db, (sql,) + tuple(rest(where_clause)))


def where(params):
    if not params:
        return ''
    return " WHERE " + " AND ".join(["{0}=%({0})s".format(k) for k in keys(params)])
