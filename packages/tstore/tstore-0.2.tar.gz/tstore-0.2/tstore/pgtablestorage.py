"""
Table storage interface to postgesql

Insert, select, update, delete rows from tables.

Run tests with:

    python -m doctest pgtablestorage.py

Make sure the current user has a 'test' DB with no password:

    createdb test


>>> import getpass
>>> user = getpass.getuser()
>>> s = DB(dbname='test', user=user, host='localhost', password='')
>>> s.execute('drop table if exists t1')
>>> s.execute('''
... create table t1 (id text not null primary key, name text, memo text)
... ''')
>>> s.select('t1')
[]
>>> s.insert('t1', {'id': 'toto', 'name': 'Toto', 'memo': 'Toto memo'})
>>> s.select('t1')
[{'memo': 'Toto memo', 'id': 'toto', 'name': 'Toto'}]
>>> s.insert('t1', {'id': 'tata', 'name': 'Tata', 'memo': 'Tata memo'})
>>> s.select('t1', ['id', 'name'])
[{'id': 'toto', 'name': 'Toto'}, {'id': 'tata', 'name': 'Tata'}]
>>> s.select('t1', where={'id': 'toto'})
[{'memo': 'Toto memo', 'id': 'toto', 'name': 'Toto'}]
>>> s.update('t1', {'memo': 'New memo'}, {'id': 'tata'})
1
>>> s.select('t1', ['memo'], where={'id': 'tata'})
[{'memo': 'New memo'}]
>>> s.delete('t1', {'name': 'Tata'})
1
>>> s.select('t1')
[{'memo': 'Toto memo', 'id': 'toto', 'name': 'Toto'}]

Dependencies:
- psycopg2 (`pip install psycopg2`)
"""

import logging
import urlparse

import psycopg2
import psycopg2.extras
import re


class DB(object):
    """PG DB interface"""
    def __init__(self, dburl=None, host=None, dbname=None, user=None,
                 password=None, autocommit=True):
        """Instantiate a new DB object.
        Needs parameters dbname, user, host, and password.
        Or, specify a DB url of the form pg://user:password@host/dbname
        If host is None or not specified, PG driver will connect using
        the default unix socket.

        You can change db.autocommit after the object has been
        instantiated.

        >>> import getpass
        >>> s = DB(dbname='test', user=getpass.getuser())
        >>> s = DB(dburl='pg://' + getpass.getuser() + ':@/test')
        >>> s = DB(dburl='mysql://:@/test')
        Traceback (most recent call last):
            ...
        ValueError: Unsupported DB scheme "mysql"
        """
        if dburl:
            (scheme, user, password, host, dbname) = parse_dburl(dburl)
            if scheme != 'pg':
                raise ValueError('Unsupported DB scheme "{}"'.format(scheme))

        self._conn = psycopg2.connect(user=user, dbname=dbname, host=host,
                                      password=password)
        self._cursor = self._conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        self.autocommit = autocommit

    def ping(self):
        """
        Return 'ok' if can ping db or raise exception

        >>> import getpass
        >>> s = DB(dbname='test', user=getpass.getuser(), host='localhost',
        ... password='')
        >>> s.ping()
        'ok'
        """
        self.execute("SELECT 1")
        return 'ok'

    def select(self, table, fields=['*'], where=None, orderby=None,
               limit=None, offset=None):
        """
        Query and return list of records.

        >>> import getpass
        >>> s = DB(dbname='test', user=getpass.getuser(), host='localhost',
        ... password='')
        >>> s.execute('drop table if exists t2')
        >>> s.execute('create table t2 (id int, name text)')
        >>> s.insert('t2', {'id': 1, 'name': 'Toto'})
        >>> rows = s.select('t2')
        >>> len(rows)
        1
        >>> row = rows[0]
        >>> row
        {'id': 1, 'name': 'Toto'}
        """
        (sql, values) = sqlselect(table, fields, where, orderby, limit, offset)
        self.execute(sql, values)
        return self.fetchall()

    def insert(self, table, row):
        """
        Add new row. Row must be a dict or implement the mapping interface.

        >>> import getpass
        >>> s = DB(dbname='test', user=getpass.getuser(), host='localhost',
        ... password='')
        >>> s.execute('drop table if exists t2')
        >>> s.execute('create table t2 (id int, name text)')
        >>> s.insert('t2', {'id': 1, 'name': 'Toto'})
        >>> rows = s.select('t2')
        >>> len(rows)
        1
        >>> row = rows[0]
        >>> row
        {'id': 1, 'name': 'Toto'}
        """
        (sql, values) = sqlinsert(table, row)
        self.execute(sql, values)

    def update(self, table, rowupdate, where):
        """
        Update matching records.
        - rowupdate is a dict with updated fields, e.g. {'name': 'John'}.
        - See `sqlwhere` for where clause.

        Returns the number of rows updated.

        >>> import getpass
        >>> s = DB(dbname='test', user=getpass.getuser(), host='localhost',
        ... password='')
        >>> s.execute('drop table if exists t2')
        >>> s.execute('create table t2 (id int, name text)')
        >>> s.insert('t2', {'id': 1, 'name': 'Toto'})
        >>> s.select('t2')
        [{'id': 1, 'name': 'Toto'}]
        >>> s.update('t2', {'name': 'Tata'}, {'id': 1})
        1
        >>> s.select('t2')
        [{'id': 1, 'name': 'Tata'}]
        """
        (sql, values) = sqlupdate(table, rowupdate, where)
        return self.execute(sql, values)

    def delete(self, table, where):
        """
        Delete matching records. Returns the number of rows deleted.
        See sqlwhere for where clause.

        >>> import getpass
        >>> s = DB(dbname='test', user=getpass.getuser(), host='localhost',
        ... password='')
        >>> s.execute('drop table if exists t2')
        >>> s.execute('create table t2 (id int, name text)')
        >>> s.insert('t2', {'id': 1, 'name': 'Toto'})
        >>> s.insert('t2', {'id': 2, 'name': 'Tata'})
        >>> s.select('t2')
        [{'id': 1, 'name': 'Toto'}, {'id': 2, 'name': 'Tata'}]
        >>> s.delete('t2', {'id': 1})
        1
        >>> s.select('t2')
        [{'id': 2, 'name': 'Tata'}]
    	"""
        (sql, values) = sqldelete(table, where)
        return self.execute(sql, values)


    # Low-level methods

    def execute(self, sql, params=None):
        """
        Execute given SQL.
        Calls `rollback` if there's a DB error and re-raises the exception.
        Calls `commit` if autocommit is True and there was no error.
        Returns number of rows affected (for commands that affect rows).

        >>> import getpass
        >>> s = DB(dbname='test', user=getpass.getuser(), host='localhost',
        ... password='')
        >>> s.execute('drop table if exists t2')
        >>> s.execute('drop table t2')
        Traceback (most recent call last):
            ...
        ProgrammingError: table "t2" does not exist
        <BLANKLINE>
        """
        logging.debug(sql)
        try:
            self._cursor.execute(sql, params)
            if self.autocommit:
                self._conn.commit()
            if self._cursor.rowcount > 0:
                return self._cursor.rowcount
        except psycopg2.Error, error:
            logging.debug('PG error ({}): {}'.format(
                error.pgcode, error.pgerror))
            self._conn.rollback()
            raise

    def commit(self):
        """
        Commit current transaction.

        >>> import getpass
        >>> s = DB(autocommit=False, dbname='test', user=getpass.getuser(),
        ... host='localhost', password='')
        >>> s.execute('drop table if exists t2')
        >>> s.execute('create table t2 (id int, name text)')
        >>> s.commit()
        >>> s.insert('t2', {'id': 1, 'name': 'Toto'})
        >>> s.select('t2')
        [{'id': 1, 'name': 'Toto'}]
        >>> # didn't commit that last one, another connection won't see it
        >>> s2 = DB(autocommit=False, dbname='test', user=getpass.getuser(),
        ... host='localhost', password='')
        >>> s2.select('t2')
        []
        >>> s.commit() # now s2 should see it
        >>> s2.select('t2')
        [{'id': 1, 'name': 'Toto'}]
        """
        self._conn.commit()

    def rollback(self):
        """
        Rollback current transaction.

        >>> import getpass
        >>> s = DB(autocommit=False, dbname='test', user=getpass.getuser(),
        ... host='localhost', password='')
        >>> s.execute('drop table if exists t2')
        >>> s.execute('create table t2 (id int, name text)')
        >>> s.commit()
        >>> s.select('t2')
        []
        >>> s.insert('t2', {'id': 1, 'name': 'Tata'})
        >>> s.select('t2')
        [{'id': 1, 'name': 'Tata'}]
        >>> s.rollback()
        >>> s.select('t2')
        []
        """
        self._conn.rollback()

    def fetchone(self):
        """
        Fetch one row from the current cursor.

        >>> import getpass
        >>> s = DB(dbname='test', user=getpass.getuser(), host='localhost',
        ... password='')
        >>> s.execute('drop table if exists t2')
        >>> s.execute('create table t2 (id int, name text)')
        >>> s.insert('t2', {'id': 1, 'name': 'Toto'})
        >>> s.execute('select * from t2')
        1
        >>> s.fetchone()
        {'id': 1, 'name': 'Toto'}
        >>> s.fetchone()
        """
        return self._cursor.fetchone()

    def fetchall(self):
        """
        Fetch all rows from the current cursor.

        >>> import getpass
        >>> s = DB(dbname='test', user=getpass.getuser(), host='localhost',
        ... password='')
        >>> s.execute('drop table if exists t2')
        >>> s.execute('create table t2 (id int, name text)')
        >>> s.insert('t2', {'id': 1, 'name': 'Toto'})
        >>> s.execute('select * from t2')
        1
        >>> s.fetchall()
        [{'id': 1, 'name': 'Toto'}]
        >>> s.fetchall()
        []
        """
        return self._cursor.fetchall()


# SQL generation

def sqlselect(table, fields=['*'], where=None, orderby=None, limit=None,
              offset=None):
    """Generates SQL select ...
    Returns (sql, params)

    >>> sqlselect('t')
    ('select * from t', [])
    >>> sqlselect('t', fields=['name', 'address'])
    ('select name, address from t', [])
    >>> sqlselect('t', where={'name': 'Toto', 'country': 'US'})
    ('select * from t where country=%s and name=%s', ['US', 'Toto'])
    >>> sqlselect('t', orderby=['lastname', 'firstname'])
    ('select * from t order by lastname, firstname', [])
    >>> sqlselect('t', limit=1)
    ('select * from t limit 1', [])
    >>> sqlselect('t', limit='yes')
    Traceback (most recent call last):
        ...
    ValueError: Limit parameter must be an int
    >>> sqlselect('t', offset=20)
    ('select * from t offset 20', [])
    >>> sqlselect('t', offset='yes')
    Traceback (most recent call last):
        ...
    ValueError: Offset parameter must be an int
    """
    validate_name(table)
    if fields != ['*']:
        validate_names(fields)
    fieldspart = ', '.join(fields)
    sql = "select {} from {}".format(fieldspart, table)
    values = []

    if where:
        (whereclause, wherevalues) = sqlwhere(where)
        if whereclause:
            sql = sql + " where " + whereclause
            values = wherevalues

    if orderby:
        validate_names(orderby)
        sql = sql + " order by " + ', '.join(orderby)

    if limit:
        if not isinstance(limit, int):
            raise ValueError("Limit parameter must be an int")
        sql = sql + " limit {}".format(limit)

    if offset:
        if not isinstance(offset, int):
            raise ValueError("Offset parameter must be an int")
        sql = sql + " offset {}".format(offset)

    return (sql, values)


def sqlinsert(table, row):
    """Generates SQL insert into table ...
    Returns (sql, parameters)

    >>> sqlinsert('mytable', {'field1': 2, 'field2': 'toto'})
    ('insert into mytable (field1, field2) values (%s, %s)', [2, 'toto'])
    >>> sqlinsert('t2', {'id': 1, 'name': 'Toto'})
    ('insert into t2 (id, name) values (%s, %s)', [1, 'Toto'])
    """
    validate_name(table)
    fields = sorted(row.keys())
    validate_names(fields)
    values = [row[field] for field in fields]
    sql = "insert into {} ({}) values ({})".format(
        table, ', '.join(fields), ', '.join(['%s'] * len(fields)))
    return sql, values


def sqlupdate(table, rowupdate, where):
    """Generates SQL update table set ...
    Returns (sql, parameters)

    >>> sqlupdate('mytable', {'field1': 3, 'field2': 'hello'}, {'id': 5})
    ('update mytable set field1=%s, field2=%s where id=%s', [3, 'hello', 5])
    """
    validate_name(table)
    fields = sorted(rowupdate.keys())
    validate_names(fields)
    values = [rowupdate[field] for field in fields]
    setparts = [field + '=%s' for field in fields]
    setclause = ', '.join(setparts)
    sql = "update {} set ".format(table) + setclause
    (whereclause, wherevalues) = sqlwhere(where)
    if whereclause:
        sql = sql + " where " + whereclause
    return (sql, values + wherevalues)


def sqldelete(table, where):
    """Generates SQL delete from ... where ...

    >>> sqldelete('t', {'id': 5})
    ('delete from t where id=%s', [5])
    """
    validate_name(table)
    (whereclause, wherevalues) = sqlwhere(where)
    sql = "delete from {}".format(table)
    if whereclause:
        sql += " where " + whereclause
    return (sql, wherevalues)


def sqlwhere(criteria=None):
    """Generates SQL where clause. Returns (sql, values).
    Criteria is a dictionary of {field: value}.

    >>> sqlwhere()
    ('', [])
    >>> sqlwhere({'id': 5})
    ('id=%s', [5])
    >>> sqlwhere({'id': 3, 'name': 'toto'})
    ('id=%s and name=%s', [3, 'toto'])
    >>> sqlwhere({'id': 3, 'name': 'toto', 'createdon': '2013-12-02'})
    ('createdon=%s and id=%s and name=%s', ['2013-12-02', 3, 'toto'])
    """
    if not criteria:
        return ('', [])
    fields = sorted(criteria.keys())
    validate_names(fields)
    values = [criteria[field] for field in fields]
    parts = [field + '=%s' for field in fields]
    sql = ' and '.join(parts)
    return (sql, values)


VALID_NAME_RE = re.compile('^[a-zA-Z0-9_]+$')


def validate_name(name):
    """Check that table/field name is valid. Raise ValueError otherwise.

    >>> validate_name('mytable')
    >>> validate_name('invalid!')
    Traceback (most recent call last):
        ...
    ValueError: Invalid name "invalid!"
    >>> validate_name('in valid')
    Traceback (most recent call last):
        ...
    ValueError: Invalid name "in valid"
    >>> validate_name('nope,nope')
    Traceback (most recent call last):
        ...
    ValueError: Invalid name "nope,nope"
    """
    if not VALID_NAME_RE.match(name):
        raise ValueError('Invalid name "{}"'.format(name))


def validate_names(names):
    """Validate list of names.

    >>> validate_names(['id', 'field'])
    >>> validate_names(['id', 'b#d'])
    Traceback (most recent call last):
        ...
    ValueError: Invalid name "b#d"
    """
    for name in names:
        validate_name(name)


def parse_dburl(dburl):
    """Parse DB URL. Return (scheme, user, password, host, dbname)
    pg://user:pass@host/dbname

    >>> parse_dburl("pg://user:pass@host/name")
    ('pg', 'user', 'pass', 'host', 'name')
    >>> parse_dburl("dbm:///dbfile")
    ('dbm', '', '', '', 'dbfile')
    >>> parse_dburl("pg://user:@/name")
    ('pg', 'user', '', '', 'name')
    """
    res = urlparse.urlparse(dburl)

    if '@' in res.netloc:
        (creds, host) = res.netloc.split('@')
    else:
        creds = ':'
        host = res.netloc

    (user, password) = creds.split(':')
    return (res.scheme, user, password, host, res.path[1:])
