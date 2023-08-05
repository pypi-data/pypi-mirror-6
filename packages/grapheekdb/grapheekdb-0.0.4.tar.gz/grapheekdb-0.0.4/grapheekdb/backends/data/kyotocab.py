# -*- coding:utf-8 -*-

try:
    import ujson as json
except ImportError:  # pragma : no cover
    import json

from kyotocabinet import DB

from grapheekdb.backends.data.base import BaseGraph
from grapheekdb.lib.exceptions import GrapheekDataException

from grapheekdb.lib.undef import UNDEFINED


class GrapheekDataKyotoCabinetException(GrapheekDataException):
    pass


class GrapheekDataKyotoCabinetInitFailureException(GrapheekDataKyotoCabinetException):
    pass


class KyotoCabinetGraph(BaseGraph):

    def __init__(self, path):
        # create the database object
        self._path = path
        self._db = DB()
        # open the database
        if not self._db.open(path, DB.OREADER | DB.OWRITER | DB.OCREATE):
            raise GrapheekDataKyotoCabinetInitFailureException(str(self._db.error()))
        super(KyotoCabinetGraph, self).__init__()
        self._ensure_prepared()
        self._closed = False

    # Start method overriding :

    def _db_close(self):
        if not self._closed:
            self._db.close()

    def _transaction_begin(self):
        self._db.begin_transaction()
        return True

    def _transaction_commit(self, txn):
        self._db.end_transaction(True)

    def _transaction_rollback(self, txn):
        self._db.end_transaction(False)

    def _has_key(self, key):
        return self._db.check(key) >= 0

    def _get(self, txn, key):
        raw_data = self._db.get(key)
        if raw_data is None:
            return UNDEFINED  # Not returning None, as None is a valid value
        return json.loads(raw_data)

    def _set(self, txn, key, value):
        return self._db.set(key, json.dumps(value))

    def _remove(self, txn, key):
        # Contrary to LocalMemoryGraph implementation, it is not needed to wrap
        # key removal in try.. except because KyotoCabinet only send "False"
        # when key does not exist
        # Thus ... _removemethod is idempotent (cf LocalMemoryGraph _remove method comment)
        self._db.remove(key)

    def _remove_prefix(self, txn, prefix):
        keys = self._db.match_prefix(prefix)
        self._db.remove_bulk(keys)

    # overriding list methods
    # looks like a bucket of hacks, and yes indeed it is :)
    # btw, it REALLY improves performance if we compare to default implementation which,
    # in the case of KyotoCabinet would involve json deserialization followed by a serialization

    def _init_lst(self, txn, key):
        self._db.set(key, '')

    def _get_lst(self, txn, key):
        value = self._db.get(key)
        if value is None:
            return UNDEFINED
        # look _append_to_lst code below to understand why a split is done
        # And why resulting list is sliced from 1
        return map(int, value.split('|')[1:])

    def _bulk_get_lst(self, txn, keys):
        dic_values = self._db.get_bulk(keys)
        results = []
        for key in keys:
            values = dic_values.get(key, UNDEFINED)
            if values == UNDEFINED:
                results.append([])
            else:
                results.append(map(int, values.split('|')[1:]))
        return results

    def _count_lst(self, txn, key):
        value = self._db.get(key)
        return value.count('|')

    def _append_to_lst(self, txn, key, value):
        self._db.append(key, '|' + str(value))

    def _remove_from_lst(self, txn, key, value):
        old = self._db.get(key)
        # Caution : we are only removing ONE occurence
        # This is voluntary
        # For instance, it lst contains neighbour node, we need to remove only one occurence
        # cause current entity and neighbour node can be linked multiple time
        new = old.replace('|%s' % value, '', 1)
        self._db.set(key, new)
