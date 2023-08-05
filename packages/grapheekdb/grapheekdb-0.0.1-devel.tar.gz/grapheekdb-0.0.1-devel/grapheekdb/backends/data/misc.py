# -*- coding:utf-8 -*-

from functools import partial

import lookups

from grapheekdb.lib.undef import UNDEFINED

from grapheekdb.backends.data.keys import build_entity_index_values, build_key
from grapheekdb.backends.data.keys import METADATA_VERTEX_INDEX_PREFIX, METADATA_EDGE_INDEX_PREFIX
from grapheekdb.backends.data.keys import KIND_VERTEX
from grapheekdb.backends.data.keys import DATA_SUFFIX

from grapheekdb.lib.exceptions import GrapheekSubLookupNotImplementedException
from grapheekdb.lib.exceptions import GrapheekInvalidLookupException


def _get_exact_filters(graph, kind, **filters):
    exact_filters = {}
    for key, value in filters.items():
        # Note : not only looking for exact lookups
        lst = key.split('__')
        len_lst = len(lst)
        if len_lst == 1:
            field = lst[0]
            clause = 'exact'
            exact_filters[field] = value
        elif len_lst == 2:
            field, clause = lst
            if clause == 'exact':
                exact_filters[field] = value
        else:
            raise GrapheekSubLookupNotImplementedException
    return exact_filters


def _get_indexed_ids_key(graph, kind, exact_filters):
    if len(exact_filters):
        METADATA_INDEX_PREFIX = METADATA_VERTEX_INDEX_PREFIX if kind == KIND_VERTEX else METADATA_EDGE_INDEX_PREFIX
        exact_filter_items = exact_filters.items()
        exact_filter_items.sort()
        fields, values = zip(*exact_filter_items)
        index_key = '/'.join([METADATA_INDEX_PREFIX] + list(fields))
        index_id = graph._get(None, index_key)
        if index_id != UNDEFINED:
            res = build_entity_index_values(kind, index_id, *values)
            return res
    return None


def _get_indexed_ids(graph, kind, **filters):
    exact_filters = _get_exact_filters(graph, kind, **filters)
    if len(exact_filters):
        indexed_ids_key = _get_indexed_ids_key(graph, kind, exact_filters)
        index_ids = graph._get_lst(None, indexed_ids_key)
        if index_ids != UNDEFINED:
            return index_ids
    return None


def build_attr_filter_funcs(**filters):
    field = clause = None
    attr_filter_funcs = []
    for key, value in filters.items():
        lst = key.split('__')
        len_lst = len(lst)
        if len_lst == 1:
            field = lst[0]
            clause = 'exact'
            lookup_func = lookups.lookup_exact
        elif len_lst == 2:
            field, clause = lst
            try:
                lookup_func = getattr(lookups, 'lookup_' + lst[1])
            except AttributeError:
                raise GrapheekInvalidLookupException
        else:
            raise GrapheekSubLookupNotImplementedException
        attr_filter_funcs.append((field, clause, partial(lookup_func, value)))
    return attr_filter_funcs


def filter_entities(graph, kind, iterator, filter_funcs, on_item=False):
    for entity_id in iterator:
        if filter_funcs:
            data = graph._get(None, build_key(kind, entity_id, DATA_SUFFIX))
            if data == UNDEFINED:  # pragma : no cover
                # This could happen because of concurrent modifications (my different process or different threads)
                # This won't normally occur when load testing with greenlets -> thus no cover
                # (or worst : direct access to backend by another "process")
                continue
            valid = True
            for field, clause, filter_func in filter_funcs:
                field_value = data.get(field, UNDEFINED)
                if field_value == UNDEFINED:
                    if clause == 'isnull':
                        field_value = None
                    else:
                        valid = False
                        break
                try:
                    valid = filter_func(field_value)
                except:
                    # Whatever happens, it shouldn't
                    # So, let's consider that data wasn't ok for the filter
                    valid = False
                if not(valid):
                    break
            if valid:
                if on_item:
                    yield graph._item_from_id(kind, entity_id)
                else:
                    yield entity_id
        else:
            # I don't do : yield item if on_item else entity_id
            # Because item is not computed (when on_item is False, this is not useful to instantiate an Entity)
            if on_item:
                yield graph._item_from_id(kind, entity_id)
            else:
                yield entity_id
