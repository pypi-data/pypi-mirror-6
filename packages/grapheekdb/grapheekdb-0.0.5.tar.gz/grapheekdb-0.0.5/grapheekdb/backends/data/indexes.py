#!/usr/bin/env
# -*- coding: utf-8 -*-

from itertools import izip_longest
from collections import defaultdict

try:
    import ujson as json
except ImportError:  # pragma : no cover
    import json


from grapheekdb.lib.undef import UNDEFINED

#from grapheekdb.backends.data.keys import METADATA_VERTEX_INDEX_PREFIX, METADATA_EDGE_INDEX_PREFIX
from grapheekdb.backends.data.keys import FORBIDDEN_KEY
from grapheekdb.backends.data.keys import CHUNK_SIZE
from grapheekdb.backends.data.keys import COUNT_SUFFIX
from grapheekdb.backends.data.keys import DATA_SUFFIX
from grapheekdb.backends.data.keys import build_key

from grapheekdb.backends.data.filtertools import _get_exact_filters

from grapheekdb.lib.exceptions import GrapheekIncompetentIndexException


def normalize_value(obj):
    return json.dumps(obj)


def choose_index_or_scan(seq_count, indexes, filters):
    """
    Helper function to choose between index use or sequential scan

    :param seq_count:
        an estimation of the sequential scan operation count (currently : number of entity_ids)
    :type seq_count:
        integer
    :param indexes:
        indexes that will challenge sequential scan. each index
        will be asked for an estimation of operation count
    :type indexes:
        BaseIndex child class instance

    :returns:
        the best index if one have been found with a probable best execution time than sequential scan
        OR None if no index was found
    """
    best_estimation = seq_count
    best_index = None
    for index in indexes:
        estimation = index.estimate(None, filters)
        if estimation < 0:  # normally : -1 (aka infinite)
            # special case : index is not competent to handle this filter
            continue
        if estimation < best_estimation:
            best_index = index
            best_estimation = estimation
    return best_index


class BaseIndex(object):

    def __init__(self, _graph, _kind, _prefix):
        self._graph = _graph
        self._kind = _kind
        self._prefix = _prefix

    def build(self, txn, id_iterator):
        raise NotImplementedError

    def add(self, txn, entity_id, data):
        raise NotImplementedError

    def remove(self, txn, entity, data):
        raise NotImplementedError

    def estimate(self, txn, filters):
        raise NotImplementedError

    def ids(self, txn, filters):
        raise NotImplementedError


class ExactIndex(BaseIndex):

    def __init__(self, _graph, _kind, _prefix, *fields):
        super(ExactIndex, self).__init__(_graph, _kind, _prefix)
        self._fields = list(fields)
        self._fields.sort()

    def build(self, txn, id_iterator):

        def save_lst(txn, chunk_idx, value, lst):
            lst_key = build_key(self._prefix, chunk_idx, value)
            self._graph._set_lst(txn, lst_key, lst)

        kind = self._kind
        values_to_id = defaultdict(list)
        # Getting data for all entity_id in chunk of <CHUNK_SIZE>
        for entity_ids in izip_longest(*([id_iterator] * CHUNK_SIZE), fillvalue=FORBIDDEN_KEY):
            entity_datas = self._graph._bulk_get(txn, [build_key(kind, entity_id, DATA_SUFFIX) for entity_id in entity_ids if entity_id != FORBIDDEN_KEY])
            for entity_key, data in entity_datas.items():
                entity_id = int(entity_key.replace(kind + '/', '').replace('/' + DATA_SUFFIX, ''))  # not very clean :(
                lst = [data.get(field, None) for field in self._fields]
                # Completing values_to_id (it's here that the reversal value -> entity_id become possible)
                values_to_id[normalize_value(lst)].append(entity_id)
        # This dic will contain the mapping entity id index key -> value chunk id
        entity_dict = {}
        for value, entity_ids in values_to_id.iteritems():
            lst = []
            value_count_key = build_key(self._prefix, COUNT_SUFFIX, value)
            value_count = 0
            self._graph._set(txn, value_count_key, 0)
            chunk_idx = 0
            for entity_id in entity_ids:
                value_count += 1
                entity_dict[build_key(self._prefix, entity_id)] = build_key(chunk_idx, value)  # Need to keep an info of relation between entity and the chunk id that contains it
                lst.append(entity_id)
                if value_count % CHUNK_SIZE == 0:
                    save_lst(txn, chunk_idx, value, lst)
                    lst = []
                    chunk_idx += 1
            if lst:
                save_lst(txn, chunk_idx, value, lst)
            self._graph._set(txn, value_count_key, value_count)
        self._graph._bulk_set(txn, entity_dict)

    def delete(self, txn):
        self._graph._remove_prefix(txn, self._prefix)

    def add(self, txn, entity_id, data):
        value = normalize_value([data.get(field, None) for field in self._fields])
        # Get current chunk idx for this value (NOTE : value is a string representing a list)
        value_count_key = build_key(self._prefix, COUNT_SUFFIX, value)
        value_count = 0
        value_count_current = self._graph._get(txn, value_count_key)
        if value_count_current != UNDEFINED:
            value_count = int(value_count_current)
        # Incrementing entity count for value
        self._graph._set(txn, value_count_key, value_count + 1)
        #  1st adding entity_id to good chunk :
        chunk_idx = value_count / CHUNK_SIZE
        chunk_key = build_key(self._prefix, chunk_idx, value)
        self._graph._append_to_lst(txn, chunk_key, entity_id)
        # Say that entity_id is in a chunk
        # (we need to keep chunk idx, so that entity id can be removed fastly
        # from chunk when entity will be removed from DB)
        self._graph._set(txn, build_key(self._prefix, entity_id), build_key(chunk_idx, value))

    def remove(self, txn, entity_id):
        entity_chunk_sub_key = self._graph._get(txn, build_key(self._prefix, entity_id))
        # remove entity_id from chunk
        chunk_key = build_key(self._prefix, entity_chunk_sub_key)
        self._graph._remove_from_lst(txn, chunk_key, entity_id)
        # Finally remove entity_chunk_sub_key
        self._graph._remove(txn, entity_chunk_sub_key)

    def estimate(self, txn, filters):
        exact_filters = _get_exact_filters(**filters)
        common_filters = dict([(k, v) for k, v in exact_filters.items() if k in self._fields])
        if len(common_filters) != len(self._fields):
            return -1  # -1 says that this index shouldn't be used
        value = normalize_value([common_filters.get(field, None) for field in self._fields])
        value_count_key = build_key(self._prefix, COUNT_SUFFIX, value)
        value_count_current = self._graph._get(txn, value_count_key)
        if value_count_current == UNDEFINED:
            return 0  # No element matching filters (from a performance point of view, that's a good news, we don't need to load any data)
        return int(value_count_current)

    def ids(self, txn, filters):
        exact_filters = _get_exact_filters(**filters)
        common_filters = dict([(k, v) for k, v in exact_filters.items() if k in self._fields])
        if len(common_filters) != len(self._fields):
            raise GrapheekIncompetentIndexException("This index should'nt have been used")
        value = normalize_value([common_filters.get(field, None) for field in self._fields])
        value_count_key = build_key(self._prefix, COUNT_SUFFIX, value)
        value_count_current = self._graph._get(txn, value_count_key)
        if value_count_current != UNDEFINED:
            for chunk_idx in range(0, 1 + int(value_count_current) / CHUNK_SIZE):
                entity_ids_key = build_key(self._prefix, chunk_idx, value)
                entity_ids = self._graph._get_lst(txn, entity_ids_key)
                if entity_ids != UNDEFINED:
                    for entity_id in entity_ids:
                        yield entity_id
