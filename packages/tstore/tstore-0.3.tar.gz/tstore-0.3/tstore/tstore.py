"""
A table-oriented storage interface

A table corresponds to a record type. From there you can
get/create/update/delete/list records.

Each record type should have an id field and metadata fields.
Metadata fields _creator, _updater, _creation_date, and _update_date
are set automatically.

Tests require the current user to have access to a DB named test
via unix socket and no password.

>>> import getpass
>>> dburl = 'pg://' + getpass.getuser() + ':@/test'
>>> sql = '''
... drop table if exists tstoretest;
... create table tstoretest(
...        id text not null primary key,
...        name text not null,
...        _creator text,
...        _creation_date timestamp,
...        _updater text,
...        _update_date timestamp);
... '''
>>> s = TStore(dburl, record_types=['tstoretest'], schemasql=sql)
>>> s.list('tstoretest')
[]
>>> s.create('tstoretest', {'id': '1', 'name': 'Toto'})
>>> len(s.list('tstoretest'))
1
>>> r = s.get('tstoretest', '1')
>>> r['name']
'Toto'
>>> s.create('tstoretest', {'id': '2', 'name': 'Tata'})
>>> len(s.list('tstoretest'))
2
>>> len(s.list('tstoretest', {'name': 'Tata'}))
1
>>> s.update('tstoretest', '1', {'name': 'Joe'})
>>> r = s.get('tstoretest', '1')
>>> r['name']
'Joe'
>>> len(s.list('tstoretest', {'name': 'Toto'}))
0
>>> s.delete('tstoretest', '2')
>>> len(s.list('tstoretest'))
1
"""

import json
import datetime
import logging

import psycopg2
import psycopg2.errorcodes

from . import pgtablestorage
from .utils import JSONEncoder


# Metadata
ID = 'id'
CREATOR = '_creator'
UPDATER = '_updater'
CREATION_DATE = '_creation_date'
UPDATE_DATE = '_update_date'


class TStore(object):
    """
    A simple table-oriented storage class.

    Override validate_record for record validation.
    """
    def __init__(self, dburl, record_types=None, schemafile=None,
                 schemasql=None, encoder=JSONEncoder):
        """
        Create new TStore object.
        - dburl: e.g. pg://user:pass@host/dbname

        Optional parameters:
        - record_types: list of acceptable record types
        - encoder: a custom JSON encoder if you use custom types
        - schemasql: string containing SQL to create schema
        - schemafile: file containing SQL to create schema
          (takes precendence over schemasql)

        >>> import getpass
        >>> s = TStore('pg://' + getpass.getuser() + ':@/test')
        """
        self._db = None
        self.dburl = dburl
        self.record_types = record_types
        self.encoder = encoder
        if schemafile:  # pragma: no cover
            schemasql = open(schemafile).read()
        if schemasql:
            self._create_schema(schemasql)

    @property
    def db(self):
        """Lazy init the DB (fork friendly)"""
        if not self._db:
            self._db = pgtablestorage.DB(dburl=self.dburl)
        return self._db

    def ping(self):
        """
        Return 'ok' if DB is reachable. Otherwise raises error.

        >>> s = teststore()
        >>> s.ping()
        'ok'
        """
        return self.db.ping()

    def get(self, cls, rid):
        """Return record of given type with key `rid`

        >>> s = teststore()
        >>> s.create('tstoretest', {'id': '1', 'name': 'Toto'})
        >>> r = s.get('tstoretest', '1')
        >>> r['name']
        'Toto'
        >>> s.get('badcls', '1')
        Traceback (most recent call last):
            ...
        ValueError: Unsupported record type "badcls"
        >>> s.get('tstoretest', '2')
        Traceback (most recent call last):
            ...
        KeyError: 'No tstoretest record with id 2'
        """
        self.validate_record_type(cls)
        rows = self.db.select(cls, where={ID: rid}, limit=1)
        if not rows:
            raise KeyError('No {} record with id {}'.format(cls, rid))
        return rows[0]

    def create(self, cls, record, user='undefined'):
        """Persist new record

        >>> s = teststore()
        >>> s.create('tstoretest', {'id': '1', 'name': 'Toto'})
        >>> s.create('tstoretest', {'id': '2', 'name': 'Tata'}, user='jane')
        >>> r = s.get('tstoretest', '2')
        >>> r[CREATOR]
        'jane'
        >>> s.create('badcls', {'id': '1', 'name': 'Toto'})
        Traceback (most recent call last):
            ...
        ValueError: Unsupported record type "badcls"
        >>> s.create('tstoretest', {'id': '1', 'name': 'Joe'})
        Traceback (most recent call last):
            ...
        KeyError: 'There is already a record for tstoretest/1'
        >>> s.create('tstoretest', {'id': '2', 'badfield': 'Joe'})
        Traceback (most recent call last):
            ...
        ValueError: Undefined field
        >>> s.create('tstoretest', {'id': '2', 'age': 'bad'})
        Traceback (most recent call last):
            ...
        ValueError: Bad record (INVALID_TEXT_REPRESENTATION)
        """
        self.validate_record(cls, record)
        record[CREATION_DATE] = record[UPDATE_DATE] = self.nowstr()
        record[CREATOR] = record[UPDATER] = user
        try:
            return self.db.insert(cls, record)
        except (psycopg2.IntegrityError, psycopg2.ProgrammingError,
                psycopg2.DataError) as error:
            logging.warning("{} {}: {}".format(
                error.__class__.__name__,
                psycopg2.errorcodes.lookup(error.pgcode), error.pgerror))
            if error.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                raise KeyError('There is already a record for {}/{}'.format(
                    cls, record[ID]))
            elif error.pgcode == psycopg2.errorcodes.UNDEFINED_COLUMN:
                raise ValueError('Undefined field')
            else:
                raise ValueError('Bad record ({})'.format(
                    psycopg2.errorcodes.lookup(error.pgcode)))

    def update(self, cls, rid, partialrecord, user='undefined'):
        """Update existing record

        >>> s = teststore()
        >>> s.create('tstoretest', {'id': '1', 'name': 'Toto'})
        >>> r = s.get('tstoretest', '1')
        >>> r['age']
        >>> s.update('tstoretest', '1', {'age': 25})
        >>> r = s.get('tstoretest', '1')
        >>> r['age']
        25
        >>> s.update('tstoretest', '1', {'age': 30}, user='jane')
        >>> r = s.get('tstoretest', '1')
        >>> r[UPDATER]
        'jane'
        >>> s.update('tstoretest', '2', {'age': 25})
        Traceback (most recent call last):
            ...
        KeyError: 'No such record'
        >>> s.create('tstoretest', {'id': '2', 'name': 'Joe'})
        >>> s.update('tstoretest', '2', {'id': '1'})
        Traceback (most recent call last):
            ...
        KeyError: 'There is already a record for tstoretest/1'
        >>> s.update('tstoretest', '2', {'badcol': '1'})
        Traceback (most recent call last):
            ...
        ValueError: Undefined field
        >>> s.update('tstoretest', '2', {'age': 'hello'})
        Traceback (most recent call last):
            ...
        ValueError: Bad update (INVALID_TEXT_REPRESENTATION)
        """
        self.validate_partial_record(cls, partialrecord)
        partialrecord[UPDATE_DATE] = self.nowstr()
        partialrecord[UPDATER] = user
        try:
            updatecount = self.db.update(cls, partialrecord, where={ID: rid})
            if updatecount < 1:
                raise KeyError('No such record')
        except (psycopg2.IntegrityError, psycopg2.ProgrammingError,
                psycopg2.DataError) as error:
            if error.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                raise KeyError('There is already a record for {}/{}'.format(
                    cls, partialrecord[ID]))
            elif error.pgcode == psycopg2.errorcodes.UNDEFINED_COLUMN:
                raise ValueError('Undefined field')
            else:
                raise ValueError('Bad update ({})'.format(
                    psycopg2.errorcodes.lookup(error.pgcode)))

    def list(self, cls, criteria=None):
        """
        Return list of matching records. criteria is a dict of {field: value}

        >>> s = teststore()
        >>> s.list('tstoretest')
        []
        """
        self.validate_criteria(cls, criteria)
        return self.db.select(cls, where=criteria)

    def delete(self, cls, rid, user='undefined'):
        """
        Delete a record by id.

        `user` currently unused. Would be used with soft deletes.

        >>> s = teststore()
        >>> s.create('tstoretest', {'id': '1', 'name': 'Toto'})
        >>> len(s.list('tstoretest'))
        1
        >>> s.delete('tstoretest', '1')
        >>> len(s.list('tstoretest'))
        0
        >>> s.delete('tstoretest', '1')
        Traceback (most recent call last):
            ...
        KeyError: 'No record tstoretest/1'
        """
        self.validate_record_type(cls)
        deletedcount = self.db.delete(cls, {ID: rid})
        if deletedcount < 1:
            raise KeyError('No record {}/{}'.format(cls, rid))

    def validate_record_type(self, cls):
        """
        Validate given record is acceptable.

        >>> s = teststore()
        >>> s.validate_record_type('tstoretest')
        >>> s.validate_record_type('bad')
        Traceback (most recent call last):
            ...
        ValueError: Unsupported record type "bad"
        """
        if self.record_types and cls not in self.record_types:
            raise ValueError('Unsupported record type "' + cls + '"')

    def as_record(self, cls, content_type, strdata):
        """
        Returns a record from serialized string representation.

        >>> s = teststore()
        >>> s.as_record('tstoretest', 'application/json',
        ... '{"id": "1", "name": "Toto"}')
        {u'id': u'1', u'name': u'Toto'}
        """
        self.validate_record_type(cls)
        parsedrecord = self.deserialize(content_type, strdata)
        return self.post_process_record(cls, parsedrecord)

    def serialize(self, cls, record):
        """
        Serialize the record to JSON. cls unused in this implementation.

        >>> s = teststore()
        >>> s.serialize('tstoretest', {'id': '1', 'name': 'Toto'})
        '{"id": "1", "name": "Toto"}'
        """
        return json.dumps(record, cls=self.encoder)

    def deserialize(self, content_type, strdata):
        """Deserialize string of given content type.

        `self` unused in this implementation.

        >>> s = teststore()
        >>> s.deserialize('application/json', '{"id": "1", "name": "Toto"}')
        {u'id': u'1', u'name': u'Toto'}
        >>> s.deserialize('text/plain', 'id: 1, name: Toto')
        Traceback (most recent call last):
            ...
        ValueError: Unsupported content type "text/plain"
        """
        if content_type != 'application/json':
            raise ValueError('Unsupported content type "' + content_type + '"')
        return json.loads(strdata)

    @staticmethod
    def nowstr():
        """Return current UTC date/time string in ISO format"""
        return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    def _create_schema(self, sql):
        "Create DB schema. Called by constructor."
        self.db.execute(sql)

    def post_process_record(self, cls, parsedrecord):
        """Post process parsed record. For example, a date field
        can be parsed into a date object.
        This default implementation doesn't do anything. Override
        as needed.
        """
        return parsedrecord

    def validate_record(self, cls, record):
        """Validate given record is proper.
        This default implementation only checks the record
        type. Override as needed.
        """
        self.validate_record_type(cls)

    def validate_partial_record(self, cls, partialrecord):
        """Validate given partial record is proper.
        A partial record is used for updates.
        This default implementation doesn't check anything.
        Override as needed.
        """
        pass

    def validate_criteria(self, cls, criteria):
        """Validate given criteria is proper for record type.
        This default implementation doesn't check anything.
        Override as needed.
        """
        pass


def teststore():
    """
    Returns test store:
    - test DB, current user, unix socket, no password
    - tstoretest table (id, name, age) + metadata

    >>> s = teststore()
    """
    logging.getLogger().setLevel(logging.CRITICAL)
    import getpass
    dburl = 'pg://' + getpass.getuser() + ':@/test'
    sql = """
    drop table if exists tstoretest;
    create table tstoretest(
        id text not null primary key,
        name text not null,
        age int,
        _creator text,
        _creation_date timestamp,
        _updater text,
        _update_date timestamp);
    """
    return TStore(dburl, record_types=['tstoretest'], schemasql=sql)
