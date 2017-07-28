"""
Contains possible and various kind of database queries
"""

# enable pragma for foreign_keys
from sqlalchemy.engine import Engine
from sqlalchemy import event, sql
from sqlalchemy.sql.expression import and_, or_, any_
import sqlite3

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.exc import DatabaseError


class ConfigDatabase(object):
    """ Describes possible fields in database structure """
    DATABASE_NAME = 'rainbow.db'
    DATABASE_URI = 'sqlite:///' + DATABASE_NAME


class HashTable:
    """Describes fields for address table"""
    TABLE_NAME = 'hash'
    COL_ID = 'id'
    COL_DECRYPTED = 'decrypted'
    COL_ENCRYPTED = 'encrypted'


engine = create_engine(ConfigDatabase.DATABASE_URI);
conn = engine.connect()
""" :type: sqlalchemy.engine.Engine """

metadata = MetaData()
hash_table = Table(HashTable.TABLE_NAME, metadata,
                   Column(HashTable.COL_ID, Integer, primary_key=True, autoincrement=True),
                   Column(HashTable.COL_DECRYPTED, String, unique=False, nullable=False),
                   Column(HashTable.COL_ENCRYPTED, String, unique=False, nullable=False),
                   )
metadata.create_all(engine)


def insert(decrypted, encrypted):
    """Inserts data to table.

    :return: If record was added as a new - :type:`bool` True. Otherwise - false
    :rtype: bool
    """
    res = None
    try:
        params = {}
        params[HashTable.COL_DECRYPTED] = decrypted
        params[HashTable.COL_ENCRYPTED] = encrypted
        ins = sql.insert(hash_table).values(**params)
        res = conn.execute(ins).rowcount > 0
        """ :type: sqlalchemy.engine.ResultProxy"""

    except DatabaseError as e:
        print("Occurs error {}".format(e))
    return res


def insertArray(array):
    """
    Inserts array of tuples

    :param list array: Array of tuples
    :return: Count of row
    """

    res = None
    try:
        params = {}
        ls = [{HashTable.COL_DECRYPTED: x[0], HashTable.COL_ENCRYPTED: x[1]} for x in array]
        res = conn.execute(hash_table.insert(), ls).rowcount > 0
        """ :type: sqlalchemy.engine.ResultProxy"""

    except DatabaseError as e:
        print("Occurs error {}".format(e))
    return res


import hashlib

accessible_symbols = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
accessible_numbers = '0123456789'
accessible_lower_case = 'abcdefghijklmnopqrstuvwxyz'


class RefInt():
    value = 0

    def increment(self):
        self.value = self.value + 1


def next_job(active_symbols, symbols, max_length=None):
    if not max_length:
        max_length = len(symbols)

    if len(active_symbols) == max_length:
        ls = []
        for s in symbols:
            new_str = active_symbols + s
            utf = new_str.encode('utf-8')
            ls.append((new_str, hashlib.sha1(utf).hexdigest()))
        insertArray(ls)
    else:
        for s in symbols:
            next_job(active_symbols + s, symbols, max_length)
