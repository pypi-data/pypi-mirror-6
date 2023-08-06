# -*- coding:utf-8 -*-

import msgpack

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
        return msgpack.loads(raw_data)

    def _bulk_get(self, txn, keys):
        result = {}
        key_raw_datas = self._db.get_bulk(keys)
        for key, raw_data in key_raw_datas.items():
            result[key] = msgpack.loads(raw_data)
        return result

    def _set(self, txn, key, value):
        res = self._db.set(key, msgpack.dumps(value))
        if not(res):  # pragma : no cover
            raise GrapheekDataKyotoCabinetException('KyotoCabinet : error while saving')
        return res

    def _bulk_set(self, txn, updates):
        dic = {}
        for key, value in updates.items():
            dic[key] = msgpack.dumps(value)
        res = self._db.set_bulk(dic)
        if res == -1:  # pragma : no cover
            raise GrapheekDataKyotoCabinetException('KyotoCabinet : error while saving')
        return res

    def _remove(self, txn, key):
        # Contrary to LocalMemoryGraph implementation, it is not needed to wrap
        # key removal in try.. except because KyotoCabinet only send "False"
        # when key does not exist
        # Thus ... _removemethod is idempotent (cf LocalMemoryGraph _remove method comment)
        self._db.remove(key)

    def _bulk_remove(self, txn, keys):
        res = self._db.remove_bulk(list(keys))
        if res == -1:  # pragma : no cover
            raise GrapheekDataKyotoCabinetException('KyotoCabinet : error while saving')
        return res

    def _remove_prefix(self, txn, prefix):
        keys = self._db.match_prefix(prefix)
        self._db.remove_bulk(keys)

    # overriding list methods
    # looks like a bucket of hacks, and yes indeed it is :)
    # btw, it REALLY improves performance if we compare to default implementation which,
    # in the case of KyotoCabinet would involve msgpack deserialization followed by a serialization

    def _init_lst(self, txn, key):
        res = self._db.set(key, '')
        if not(res):  # pragma : no cover
            raise GrapheekDataKyotoCabinetException('KyotoCabinet : error while saving')
        return res

    def _get_lst(self, txn, key):
        value = self._db.get(key)
        if value is None:
            return UNDEFINED
        # look _append_to_lst code below to understand why a split is done
        # And why resulting list is sliced from 1
        return map(int, value.split('|')[1:])

    def _set_lst(self, txn, key, values):
        newval = '|'.join([str(value) for value in values])
        res = self._db.set(key, '|' + newval)
        if not(res):  # pragma : no cover
            raise GrapheekDataKyotoCabinetException('KyotoCabinet : error while saving')
        return res

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

    def _append_to_lst(self, txn, key, value):
        self._db.append(key, '|' + str(value))

    def _bulk_append_to_lst(self, txn, key, values):
        newval = '|'.join([str(value) for value in values])
        self._db.append(key, '|' + newval)

    def _remove_from_lst(self, txn, key, value):
        old = self._db.get(key)
        # Caution : we are only removing ONE occurence
        # This is voluntary
        # For instance, it lst contains neighbour node, we need to remove only one occurence
        # cause current entity and neighbour node can be linked multiple time
        new = old.replace('|%s' % value, '', 1)
        if new == old:
            raise ValueError("list.remove(x): x not in list")
        res = self._db.set(key, new)
        if not(res):  # pragma : no cover
            raise GrapheekDataKyotoCabinetException('KyotoCabinet : error while saving')
        return res

    def _bulk_remove_from_lst(self, txn, key, values):
        old = self._db.get(key)
        assert(len(values))
        new = old
        for value in values:
            new = new.replace('|%s' % value, '', 1)
        if new == old:  # pragma : no cover
            raise ValueError("list.remove(x): x not in list")
        res = self._db.set(key, new)
        if not(res):  # pragma : no cover
            raise GrapheekDataKyotoCabinetException('KyotoCabinet : error while saving')
        return res
