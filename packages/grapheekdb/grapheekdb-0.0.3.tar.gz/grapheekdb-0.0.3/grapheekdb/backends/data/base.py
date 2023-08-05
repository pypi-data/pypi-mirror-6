# -*- coding:utf-8 -*-

from types import DictType
from collections import defaultdict

from grapheekdb.lib.undef import UNDEFINED
from grapheekdb.lib.readwrite import GraphReadWrite

from grapheekdb.backends.data.keys import PREPARED
from grapheekdb.backends.data.keys import METADATA_EDGE_COUNTER, METADATA_EDGE_INDEX_COUNTER, METADATA_EDGE_INDEX_LIST, METADATA_EDGE_INDEX_FIELDS_PREFIX, METADATA_EDGE_INDEX_PREFIX
from grapheekdb.backends.data.keys import METADATA_VERTEX_COUNTER, METADATA_VERTEX_INDEX_COUNTER, METADATA_VERTEX_INDEX_LIST, METADATA_VERTEX_INDEX_FIELDS_PREFIX, METADATA_VERTEX_INDEX_PREFIX
from grapheekdb.backends.data.keys import build_entity_index_values, build_entity_index_prefix
from grapheekdb.backends.data.keys import build_key
from grapheekdb.backends.data.keys import DATA_SUFFIX
from grapheekdb.backends.data.keys import IN_EDGES_SUFFIX, IN_VERTICES_SUFFIX
from grapheekdb.backends.data.keys import OUT_EDGES_SUFFIX, OUT_VERTICES_SUFFIX
from grapheekdb.backends.data.keys import BOTH_EDGES_SUFFIX, BOTH_VERTICES_SUFFIX
from grapheekdb.backends.data.keys import COUNT_SUFFIX
from grapheekdb.backends.data.keys import KIND_VERTEX, KIND_EDGE
#from grapheekdb.backends.data.keys import VERTEX_DATA_REGEXP, EDGE_DATA_REGEXP
#from grapheekdb.backends.data.keys import VERTEX_DATA_PATTERN, EDGE_DATA_PATTERN
from grapheekdb.backends.data.keys import METADATA_EDGE_ID_LIST_PREFIX, METADATA_VERTEX_ID_LIST_PREFIX
from grapheekdb.backends.data.keys import ID_LIST_MODULO

from grapheekdb.lib.validations import check_valid_data

from grapheekdb.lib.exceptions import GrapheekDataException
from grapheekdb.lib.exceptions import GrapheekDataPreparationFailedException
from grapheekdb.lib.exceptions import GrapheekIndexAlreadyExistsException
from grapheekdb.lib.exceptions import GrapheekIndexCreationFailedException
from grapheekdb.lib.exceptions import GrapheekIndexRemovalFailedException
from grapheekdb.lib.exceptions import GrapheekNoSuchTraversalException
from grapheekdb.lib.exceptions import GrapheekMissingKeyException
from grapheekdb.lib.exceptions import GrapheekInvalidDataTypeException
from grapheekdb.lib.exceptions import GrapheekUnknownScriptException

from grapheekdb.backends.data.misc import build_attr_filter_funcs
from grapheekdb.backends.data.misc import _get_exact_filters
from grapheekdb.backends.data.misc import _get_indexed_ids_key
from grapheekdb.backends.data.misc import _get_indexed_ids
from grapheekdb.backends.data.misc import filter_entities


# misc iterator :
def _jump_iterator(_graph, _kind, _entity_id_iterator, _traversal, _neighbors_cache, **filters):
    for entity_id in _entity_id_iterator:
        for neighbor_id in iter(_graph._neighbors(_kind, entity_id, _traversal, _neighbors_cache, **filters)):
            yield neighbor_id


def check_base_node(entity):
    if not(isinstance(entity, Node)):
        raise GrapheekInvalidDataTypeException('%s is not a node')


def check_and_get_count(args):
    count_args = len(args)
    assert(count_args < 2)
    # how many recursive jumps ? :
    count = 1
    if count_args == 1:
        count = int(args[0])
        assert(count >= 0)
    return count


def get_kind_ids(graph, txn, kind):
    ENTITY_COUNTER = METADATA_VERTEX_COUNTER if kind == KIND_VERTEX else METADATA_EDGE_COUNTER
    METADATA_ID_LIST_PREFIX = METADATA_VERTEX_ID_LIST_PREFIX if kind == KIND_VERTEX else METADATA_EDGE_ID_LIST_PREFIX
    limit = int(graph._get(None, ENTITY_COUNTER)) / ID_LIST_MODULO
    keys = [build_key(METADATA_ID_LIST_PREFIX, i) for i in range(0, limit + 1)]
    list_entity_ids = graph._bulk_get_lst(txn, keys)
    for entity_ids in list_entity_ids:
        if entity_ids != UNDEFINED:
            for entity_id in entity_ids:
                yield entity_id


class DotExport(object):
    """
    This class is mainly intended to be used with an IPython Graphviz Magics extension
    You can start IPython by launching in a shell
    ipython notebook

    Then create a new notebook and install extension :
    %install_ext https://raw.github.com/cjdrake/ipython-magic/master/gvmagic.py

    Load extension :
    %load_ext gvmagic

    Then you can see an entity iterator by doing, for instance :
    %dotobj g.V(...).dot()

    The EntityIterator.dot method instantiates a DotExport which itself has a .to_dot method as expected by gvmagic...
    """

    def __init__(self, entity_iterator, node_label=None, edge_label=None, limit=100):
        self._entity_iterator = entity_iterator
        self._graph = entity_iterator._graph
        self.node_label = node_label
        self.edge_label = edge_label
        self.limit = int(limit)
        assert(self.limit > 0)

    def __str__(self):
        return self.to_dot()

    def _clean_label(self, label):
        import re
        s = re.sub('[^0-9a-zA-Z_\s]', '', str(label))  # Needs sth less intrusive
        return s

    def _node_label(self, node_id):
        node = Node(node_id, self._graph)
        label = str(node_id)  # Default value
        if self.node_label is not None:
            label = node.data().get(self.node_label, label)
        return self._clean_label(label)

    def _edge_struct(self, edge_id):
        edge = Edge(edge_id, self._graph)
        label = ''  # Default value
        if self.edge_label is not None:
            label = edge.data().get(self.edge_label, label)
        # get src and tgt node ids :
        src_id = edge._src_id()
        tgt_id = edge._tgt_id()
        return (self._clean_label(label), src_id, tgt_id)

    def to_dot(self):
        entity_iterator = self._entity_iterator
        kind = entity_iterator._src_kind
        assert(kind in [KIND_VERTEX, KIND_EDGE])
        node_collections = []
        edge_collections = []
        if kind == KIND_EDGE:
            # Collecting label, ids and related node ids :
            edge_node_ids    = set()
            for edge_id in set(entity_iterator.limit(self.limit)._iterate(on_item=False)):
                label, src_id, tgt_id = self._edge_struct(edge_id)
                edge_collections.append((label, src_id, tgt_id))
                edge_node_ids.add(src_id)
                edge_node_ids.add(tgt_id)
            # Collecting nodes :
            for node_id in edge_node_ids:
                label = self._node_label(node_id)
                node_collections.append((node_id, label))
        else:  # KIND_VERTEX
            node_edge_ids    = set()
            node_ids = set(entity_iterator.limit(self.limit)._iterate(on_item=False))
            # Collecting label, ids and related edge ids :
            for node_id in node_ids:
                label = self._node_label(node_id)
                node_collections.append((node_id, label))
                for edge_id in self._graph._neighbors(KIND_VERTEX, node_id, BOTH_EDGES_SUFFIX):
                    if not edge_id in node_edge_ids:
                        edge_label, edge_src_id, edge_tgt_id = self._edge_struct(edge_id)
                        if (edge_src_id in node_ids) and (edge_tgt_id in node_ids):
                            edge_collections.append((edge_label, edge_src_id, edge_tgt_id))
                            node_edge_ids.add(edge_id)
        # Finally build the dot string :
        lines = []
        lines.append('digraph G {')
        for node_id, label in node_collections:
            lines.append('"n%s" [' % node_id)
            lines.append('label ="%s"' % label)
            lines.append('];')
        for label, src_id, tgt_id in edge_collections:
            lines.append('"n%s" -> "n%s" [label="%s"]' % (src_id, tgt_id, label))
        lines.append('}')
        return '\n'.join(lines)


class EntityIterator(object):

    def __init__(self, graph, src_kind, filters, id_iterator, parent=None, neighbors_cache=None, context=None):
        assert(id_iterator is not None)
        self._graph = graph
        self._src_kind = src_kind
        self._filters = filters
        self._attr_filter_funcs = build_attr_filter_funcs(**filters)
        self._id_iterator = id_iterator
        self._parent = parent
        self._neighbors_cache = neighbors_cache if neighbors_cache is not None else {}
        self._release_neighbors_cache = neighbors_cache is None
        if context is None:
            self._context = {} if parent is None else parent._context
        else:
            self._context = context
        self._current_iteration = None

    def _finalize(self):
        if self._release_neighbors_cache:
            # Implicit cache removal
            self._neighbors_cache = {}

    def _iterate(self, on_item=False):
        for item in filter_entities(self._graph, self._src_kind, self._id_iterator, self._attr_filter_funcs, on_item):
            yield item
        self._finalize()

    def __iter__(self):
        return self

    def _jump(self, _kind, _traversal, *args, **filters):
        # TODO : Refactor this function : it can certainly be rewritten in a far easier way
        count = check_and_get_count(args)
        current_iterator = self
        parent_kind = self._src_kind
        current_kind = _kind
        current_parent = self
        # (potentially) recursive jumping
        #_jump_iterator(graph, kind, entity_id_iterator, traversal, neighbors_cache, filters)
        for _ in range(count):
            current_iterator = EntityIterator(
                self._graph,
                current_kind,
                filters,
                _jump_iterator(
                    self._graph,
                    parent_kind,
                    current_iterator._iterate(),
                    _traversal,
                    self._neighbors_cache,
                    **filters
                ),
                parent=current_parent
            )
            parent_kind = current_kind
            current_kind = KIND_VERTEX
            current_parent = current_iterator
        return current_iterator

    def next(self):
        if self._current_iteration is None:
            self._current_iteration = self._iterate(on_item=True)
        try:
            return self._current_iteration.next()
        except StopIteration:
            self._current_iteration = None
        raise StopIteration

    def inV(self, *args, **filters):
        return self._jump(KIND_VERTEX, IN_VERTICES_SUFFIX, *args, **filters)

    def outV(self, *args, **filters):
        return self._jump(KIND_VERTEX, OUT_VERTICES_SUFFIX, *args, **filters)

    def bothV(self, *args, **filters):
        return self._jump(KIND_VERTEX, BOTH_VERTICES_SUFFIX, *args, **filters)

    def IN(self, *args, **filters):
        assert(self._src_kind == KIND_VERTEX)
        count = check_and_get_count(args)
        if count == 1:
            return self.inE(**filters).inV()
        return self.IN(count - 1, **filters).inE(*args, **filters).inV()

    def OUT(self, *args, **filters):
        assert(self._src_kind == KIND_VERTEX)
        count = check_and_get_count(args)
        if count == 1:
            return self.outE(**filters).outV()
        return self.OUT(count - 1, **filters).outE(*args, **filters).outV()

    def BOTH(self, *args, **filters):
        assert(self._src_kind == KIND_VERTEX)
        count = check_and_get_count(args)

        def neighbor_iterator(graph, it, filters, neighbors_cache, filter_funcs):
            entity_ids = list(it)
            for entity_id in entity_ids:
                neighbor_edge_id_iterator = graph._neighbors(KIND_VERTEX, entity_id, OUT_EDGES_SUFFIX, neighbors_cache, **filters)
                for neighbor_edge_id in filter_entities(self._graph, KIND_EDGE, neighbor_edge_id_iterator, filter_funcs):
                    for neighbor_node_id in graph._neighbors(KIND_EDGE, neighbor_edge_id, OUT_VERTICES_SUFFIX, neighbors_cache):
                        if int(entity_id) != int(neighbor_node_id):
                            yield neighbor_node_id
            for entity_id in entity_ids:
                neighbor_edge_id_iterator = graph._neighbors(KIND_VERTEX, entity_id, IN_EDGES_SUFFIX, neighbors_cache, **filters)
                for neighbor_edge_id in filter_entities(self._graph, KIND_EDGE, neighbor_edge_id_iterator, filter_funcs):
                    for neighbor_node_id in graph._neighbors(KIND_EDGE, neighbor_edge_id, IN_VERTICES_SUFFIX, neighbors_cache):
                        if int(entity_id) != int(neighbor_node_id):
                            yield neighbor_node_id

        filter_funcs = build_attr_filter_funcs(**filters)
        if count == 1:
            return EntityIterator(
                self._graph,
                KIND_VERTEX,
                {},
                neighbor_iterator(self._graph, self._iterate(), filters, self._neighbors_cache, filter_funcs),
                parent=self,
                neighbors_cache=self._neighbors_cache
            )
        entity_iterator = self.BOTH(count - 1, **filters)
        return EntityIterator(
            self._graph,
            KIND_VERTEX,
            {},
            neighbor_iterator(self._graph, entity_iterator._iterate(), filters, self._neighbors_cache, filter_funcs),
            parent=entity_iterator,
            neighbors_cache=self._neighbors_cache
        )

    # NOTE : for xxE methods, below, there's no *args :
    # currently *args is aimed to contain only number of jumps
    # so only 1st item of args is used
    # if args is empty, only one jump is done
    # So this is "recursive" jumping
    # But chaining xxE methods wouldn't make sense as Edge outer entities are always Nodes

    def inE(self, *args, **filters):
        if self._src_kind == KIND_EDGE:
            raise GrapheekNoSuchTraversalException
        return self._jump(KIND_EDGE, IN_EDGES_SUFFIX, **filters)  # no *args for inE ()

    def outE(self, *args, **filters):
        if self._src_kind == KIND_EDGE:
            raise GrapheekNoSuchTraversalException
        return self._jump(KIND_EDGE, OUT_EDGES_SUFFIX, **filters)

    def bothE(self, *args, **filters):
        if self._src_kind == KIND_EDGE:
            raise GrapheekNoSuchTraversalException
        return self._jump(KIND_EDGE, BOTH_EDGES_SUFFIX, **filters)

    def dedup(self):
        def dedup_iterator(entity_iterator):
            known = set()
            for entity_id in entity_iterator:
                if entity_id in known:
                    continue
                known.add(entity_id)
                yield entity_id
        return EntityIterator(self._graph, self._src_kind, {}, dedup_iterator(self._iterate()), parent=self)

    def idata(self):
        for item in self:
            yield item.data()

    def data(self):
        return list(self.idata())

    def limit(self, count):
        def limit_iterator(entity_id_iterator, count):
            counter = 0
            for entity_id in entity_id_iterator:
                if counter < count:
                    yield entity_id
                else:
                    break  # This line is REALLY important (it stops outer iteration)
                counter += 1
        return EntityIterator(self._graph, self._src_kind, {}, limit_iterator(self._iterate(), count), parent=self)

    def aka(self, alias):
        def alias_iterator(entity_iterator, alias):
            for entity in entity_iterator:
                self._context[alias] = entity
                yield entity.get_id()
        return EntityIterator(self._graph, self._src_kind, {}, alias_iterator(self, alias), parent=self)

    # Following methods don't return iterator :

    def count(self):
        return sum(1 for _ in self._iterate())  # space efficient counter

    def remove(self):
        remove_func = self._graph._remove_node if self._src_kind == KIND_VERTEX else self._graph._remove_edge
        for entity_id in self._iterate():
            remove_func(entity_id)

    def update(self, **updates):
        # Do the update (not done while iterating because *every* entity must be updated before starting to yield)
        txn = self._graph._transaction_begin()
        try:
            for entity_id in self._iterate(on_item=False):
                self._graph._bulk_update_data(txn, self._src_kind, entity_id, **updates)
            self._graph._transaction_commit(txn)
        except Exception, e:
            self._graph._transaction_rollback(txn)
            raise GrapheekDataException(repr(e))

    def collect(self, *args):
        result = []
        for entity in self:
            result.append([self._context.get(alias, None) for alias in args])
        return result

    def agg(self, aggtype='+', asc=False):
        assert(aggtype in ['+', '%'])
        mult = 1 if asc else -1
        counters = defaultdict(int)
        total = 0
        for entity_id in self._iterate():
            counters[entity_id] += 1
            total += 1
        if total and (aggtype == '%'):
            for entity_id, value in counters.items():
                counters[entity_id] = float(counters[entity_id]) / float(total)
        ordered_counters = sorted(counters.items(), key=lambda t: t[1] * mult)
        return [(self._graph._item_from_id(self._src_kind, entity_id), count) for entity_id, count in ordered_counters]

    def call(self, _fname, *aliases, **params):
        for entity_id in self._iterate():  # Iterating updates the context ...
            self._graph._call_server_script(self._context, _fname, *aliases, **params)

    def request(self, _fname, *aliases, **params):
        # Same as call but returns results of each call
        results = []
        for entity_id in self._iterate():  # Iterating updates the context ...
            results.append(self._graph._call_server_script(self._context, _fname, *aliases, **params))
        return results

    def dot(self, node_label=None, edge_label=None, limit=100):
        return DotExport(self, node_label, edge_label, limit)

    def _dot_str(self, node_label=None, edge_label=None, limit=100):
        return str(DotExport(self, node_label, edge_label, limit))


class Entity(object):

    def __init__(self, entity_id, graph):
        self._entity_id = int(entity_id)  # Depending on backend, sometimes, id are stored as string
        self._graph = graph

    def __repr__(self):
        kind = 'node' if self._kind == KIND_VERTEX else 'edge'
        return '<%s id:%s data:%s>' % (kind, self._entity_id, repr(self.data()))

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other.get_id() == self.get_id() and other._graph == self._graph

    def __ne__(self, other):
        # Cf Python Doc : http://docs.python.org/2/reference/datamodel.html#object.__ne__
        # "When defining __eq__(), one should also define __ne__() so that the operators will behave as expected"
        return not self.__eq__(other)

    def __getattr__(self, attr):
        try:
            return self._graph._get_data(None, self._kind, self._entity_id)[attr]
        except KeyError:
            raise AttributeError("%r instance has no attribute %r" % (self.__class__, attr))

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            self.__dict__.update({attr: value})
        else:
            self._graph._update_data(self._kind, self._entity_id, attr, value)

    def _neighbors(self, _traversal, **filters):
        return self._graph._neighbors(self._kind, self._entity_id, _traversal, **filters)

    def _jump(self, _tgt_kind, _traversal, *args, **filters):
        # TODO : Factor code with EntityIterator._jump
        count_args = len(args)
        assert(count_args < 2)
        # how many recursive jumps ? :
        count = 1
        if count_args == 1:
            count = args[0]
        current_iterator = self._neighbors(_traversal, **filters)
        parent_kind = self._kind
        current_kind = _tgt_kind
        current_parent = None
        # (potentially) recursive jumping
        for i in range(count):
            IT = current_iterator if i == 0 else _jump_iterator(self._graph, parent_kind, current_iterator._iterate(), _traversal, {}, **filters)
            current_iterator = EntityIterator(
                self._graph,
                current_kind,
                filters,
                IT,
                parent=current_parent
            )
            parent_kind = current_kind
            current_kind = KIND_VERTEX
            current_parent = current_iterator
        return current_iterator

    def inV(self, *args, **filters):
        return self._jump(KIND_VERTEX, IN_VERTICES_SUFFIX, *args, **filters)

    def outV(self, *args, **filters):
        return self._jump(KIND_VERTEX, OUT_VERTICES_SUFFIX, *args, **filters)

    def bothV(self, *args, **filters):
        return self._jump(KIND_VERTEX, BOTH_VERTICES_SUFFIX, *args, **filters)

    def data(self):
        return self._graph._get_data(None, self._kind, self._entity_id)

    def get_id(self):
        return self._entity_id

    def update(self, **updates):
        self._graph._bulk_update_data(None, self._kind, self._entity_id, **updates)

    def aka(self, alias):
        def self_iterator(entity_id):
            yield entity_id
        return EntityIterator(self._graph, self._kind, {}, self_iterator(self.get_id()), context={alias: self})


class Node(Entity):

    def __init__(self, entity_id, graph):
        super(Node, self).__init__(entity_id, graph)
        self._kind = KIND_VERTEX

    def __change_denorm_data(self, txn, lst_operation, counter_operation, *counter_args):
        node_id = self._entity_id
        # traversal denormalized lists
        lst_operation(txn, build_key(KIND_VERTEX, node_id, IN_EDGES_SUFFIX))
        lst_operation(txn, build_key(KIND_VERTEX, node_id, IN_VERTICES_SUFFIX))
        lst_operation(txn, build_key(KIND_VERTEX, node_id, OUT_EDGES_SUFFIX))
        lst_operation(txn, build_key(KIND_VERTEX, node_id, OUT_VERTICES_SUFFIX))
        lst_operation(txn, build_key(KIND_VERTEX, node_id, BOTH_EDGES_SUFFIX))
        lst_operation(txn, build_key(KIND_VERTEX, node_id, BOTH_VERTICES_SUFFIX))
        # traversal denormalized counters
        counter_operation(txn, build_key(KIND_VERTEX, node_id, IN_EDGES_SUFFIX, COUNT_SUFFIX), *counter_args)
        counter_operation(txn, build_key(KIND_VERTEX, node_id, IN_VERTICES_SUFFIX, COUNT_SUFFIX), *counter_args)
        counter_operation(txn, build_key(KIND_VERTEX, node_id, OUT_EDGES_SUFFIX, COUNT_SUFFIX), *counter_args)
        counter_operation(txn, build_key(KIND_VERTEX, node_id, OUT_VERTICES_SUFFIX, COUNT_SUFFIX), *counter_args)
        counter_operation(txn, build_key(KIND_VERTEX, node_id, BOTH_EDGES_SUFFIX, COUNT_SUFFIX), *counter_args)
        counter_operation(txn, build_key(KIND_VERTEX, node_id, BOTH_VERTICES_SUFFIX, COUNT_SUFFIX), *counter_args)

    def _add_denorm_data(self, txn):
        self.__change_denorm_data(txn, self._graph._init_lst, self._graph._set, 0)

    def _remove_denorm_data(self, txn):
        self.__change_denorm_data(txn, self._graph._remove, self._graph._remove)

    def _add_denorm_src_data(self, txn, target, edge):
        graph = self._graph
        source_id = self._entity_id
        target_id = target.get_id()
        edge_id = edge.get_id()
        # lists
        graph._append_to_lst(txn, build_key(KIND_VERTEX, source_id, OUT_EDGES_SUFFIX), edge_id)
        graph._append_to_lst(txn, build_key(KIND_VERTEX, source_id, BOTH_EDGES_SUFFIX), edge_id)
        graph._append_to_lst(txn, build_key(KIND_VERTEX, source_id, OUT_VERTICES_SUFFIX), target_id)
        graph._append_to_lst(txn, build_key(KIND_VERTEX, source_id, BOTH_VERTICES_SUFFIX), target_id)
        # counters
        graph._update_inc(txn, build_key(KIND_VERTEX, source_id, OUT_EDGES_SUFFIX, COUNT_SUFFIX))
        graph._update_inc(txn, build_key(KIND_VERTEX, source_id, BOTH_EDGES_SUFFIX, COUNT_SUFFIX))
        graph._update_inc(txn, build_key(KIND_VERTEX, source_id, OUT_VERTICES_SUFFIX, COUNT_SUFFIX))
        graph._update_inc(txn, build_key(KIND_VERTEX, source_id, BOTH_VERTICES_SUFFIX, COUNT_SUFFIX))
        # create a key/value for links between source and target (aimed to be used with indexes)
        graph._set(txn, build_key(KIND_VERTEX, source_id, OUT_EDGES_SUFFIX, edge_id), 1)
        graph._set(txn, build_key(KIND_VERTEX, source_id, BOTH_EDGES_SUFFIX, edge_id), 1)
        graph._set(txn, build_key(KIND_VERTEX, source_id, OUT_VERTICES_SUFFIX, target_id), 1)
        graph._set(txn, build_key(KIND_VERTEX, source_id, BOTH_VERTICES_SUFFIX, target_id), 1)

    def _remove_denorm_src_data(self, txn, target, edge):
        graph = self._graph
        source_id = self._entity_id
        target_id = target.get_id()
        edge_id = edge.get_id()
        # lists
        graph._remove_from_lst(txn, build_key(KIND_VERTEX, source_id, OUT_EDGES_SUFFIX), edge_id)
        graph._remove_from_lst(txn, build_key(KIND_VERTEX, source_id, BOTH_EDGES_SUFFIX), edge_id)
        graph._remove_from_lst(txn, build_key(KIND_VERTEX, source_id, OUT_VERTICES_SUFFIX), target_id)
        graph._remove_from_lst(txn, build_key(KIND_VERTEX, source_id, BOTH_VERTICES_SUFFIX), target_id)
        # counters
        graph._update_dec(txn, build_key(KIND_VERTEX, source_id, OUT_EDGES_SUFFIX, COUNT_SUFFIX))
        graph._update_dec(txn, build_key(KIND_VERTEX, source_id, BOTH_EDGES_SUFFIX, COUNT_SUFFIX))
        graph._update_dec(txn, build_key(KIND_VERTEX, source_id, OUT_VERTICES_SUFFIX, COUNT_SUFFIX))
        graph._update_dec(txn, build_key(KIND_VERTEX, source_id, BOTH_VERTICES_SUFFIX, COUNT_SUFFIX))
        # create a key/value for links between source and target (aimed to be used with indexes)
        graph._remove(txn, build_key(KIND_VERTEX, source_id, OUT_EDGES_SUFFIX, edge_id))
        graph._remove(txn, build_key(KIND_VERTEX, source_id, BOTH_EDGES_SUFFIX, edge_id))
        graph._remove(txn, build_key(KIND_VERTEX, source_id, OUT_VERTICES_SUFFIX, target_id))
        graph._remove(txn, build_key(KIND_VERTEX, source_id, BOTH_VERTICES_SUFFIX, target_id))

    def _add_denorm_tgt_data(self, txn, source, edge):
        graph = self._graph
        target_id = self._entity_id
        source_id = source.get_id()
        edge_id = edge.get_id()
        # lists
        graph._append_to_lst(txn, build_key(KIND_VERTEX, target_id, IN_EDGES_SUFFIX), edge_id)
        graph._append_to_lst(txn, build_key(KIND_VERTEX, target_id, BOTH_EDGES_SUFFIX), edge_id)
        graph._append_to_lst(txn, build_key(KIND_VERTEX, target_id, IN_VERTICES_SUFFIX), source_id)
        graph._append_to_lst(txn, build_key(KIND_VERTEX, target_id, BOTH_VERTICES_SUFFIX), source_id)
        # counters
        graph._update_inc(txn, build_key(KIND_VERTEX, target_id, IN_EDGES_SUFFIX, COUNT_SUFFIX))
        graph._update_inc(txn, build_key(KIND_VERTEX, target_id, BOTH_EDGES_SUFFIX, COUNT_SUFFIX))
        graph._update_inc(txn, build_key(KIND_VERTEX, target_id, IN_VERTICES_SUFFIX, COUNT_SUFFIX))
        graph._update_inc(txn, build_key(KIND_VERTEX, target_id, BOTH_VERTICES_SUFFIX, COUNT_SUFFIX))
        # create a key/value for links between source and target (aimed to be used with indexes)
        graph._set(txn, build_key(KIND_VERTEX, target_id, IN_EDGES_SUFFIX, edge_id), 1)
        graph._set(txn, build_key(KIND_VERTEX, target_id, BOTH_EDGES_SUFFIX, edge_id), 1)
        graph._set(txn, build_key(KIND_VERTEX, target_id, IN_VERTICES_SUFFIX, source_id), 1)
        graph._set(txn, build_key(KIND_VERTEX, target_id, BOTH_VERTICES_SUFFIX, source_id), 1)

    def _remove_denorm_tgt_data(self, txn, source, edge):
        graph = self._graph
        target_id = self._entity_id
        source_id = source.get_id()
        edge_id = edge.get_id()
        # lists
        graph._remove_from_lst(txn, build_key(KIND_VERTEX, target_id, IN_EDGES_SUFFIX), edge_id)
        graph._remove_from_lst(txn, build_key(KIND_VERTEX, target_id, BOTH_EDGES_SUFFIX), edge_id)
        graph._remove_from_lst(txn, build_key(KIND_VERTEX, target_id, IN_VERTICES_SUFFIX), source_id)
        graph._remove_from_lst(txn, build_key(KIND_VERTEX, target_id, BOTH_VERTICES_SUFFIX), source_id)
        # counters
        graph._update_dec(txn, build_key(KIND_VERTEX, target_id, IN_EDGES_SUFFIX, COUNT_SUFFIX))
        graph._update_dec(txn, build_key(KIND_VERTEX, target_id, BOTH_EDGES_SUFFIX, COUNT_SUFFIX))
        graph._update_dec(txn, build_key(KIND_VERTEX, target_id, IN_VERTICES_SUFFIX, COUNT_SUFFIX))
        graph._update_dec(txn, build_key(KIND_VERTEX, target_id, BOTH_VERTICES_SUFFIX, COUNT_SUFFIX))
        # create a key/value for links between source and target (aimed to be used with indexes)
        graph._remove(txn, build_key(KIND_VERTEX, target_id, IN_EDGES_SUFFIX, edge_id))
        graph._remove(txn, build_key(KIND_VERTEX, target_id, BOTH_EDGES_SUFFIX, edge_id))
        graph._remove(txn, build_key(KIND_VERTEX, target_id, IN_VERTICES_SUFFIX, source_id))
        graph._remove(txn, build_key(KIND_VERTEX, target_id, BOTH_VERTICES_SUFFIX, source_id))

    def IN(self, *args, **filters):
        def self_iterator(entity_id):
            yield entity_id
        entity_iterator = EntityIterator(self._graph, KIND_VERTEX, {}, self_iterator(self.get_id()), context={})
        return entity_iterator.IN(*args, **filters)

    def OUT(self, *args, **filters):
        def self_iterator(entity_id):
            yield entity_id
        entity_iterator = EntityIterator(self._graph, KIND_VERTEX, {}, self_iterator(self.get_id()), context={})
        return entity_iterator.OUT(*args, **filters)

    def BOTH(self, *args, **filters):
        def self_iterator(entity_id):
            yield entity_id
        entity_iterator = EntityIterator(self._graph, KIND_VERTEX, {}, self_iterator(self.get_id()), context={})
        return entity_iterator.BOTH(*args, **filters)

    def inE(self, **filters):
        return self._jump(KIND_EDGE, IN_EDGES_SUFFIX, **filters)

    def outE(self, **filters):
        return self._jump(KIND_EDGE, OUT_EDGES_SUFFIX, **filters)

    def bothE(self, **filters):
        return self._jump(KIND_EDGE, BOTH_EDGES_SUFFIX, **filters)

    def remove(self):
        self._graph._remove_node(self._entity_id)


class Edge(Entity):

    def __init__(self, entity_id, graph):
        super(Edge, self).__init__(entity_id, graph)
        self._kind = KIND_EDGE

    def _src_id(self):
        return self._graph._get_lst(None, build_key(KIND_EDGE, self._entity_id, IN_VERTICES_SUFFIX))[0]

    def _tgt_id(self):
        return self._graph._get_lst(None, build_key(KIND_EDGE, self._entity_id, OUT_VERTICES_SUFFIX))[0]

    def _add_denorm_data(self, txn, source, target):
        edge_id = self._entity_id
        source_id = source.get_id()
        target_id = target.get_id()
        # traversal denormalized lists
        self._graph._append_to_lst(txn, build_key(KIND_EDGE, edge_id, IN_VERTICES_SUFFIX), source_id)
        self._graph._append_to_lst(txn, build_key(KIND_EDGE, edge_id, OUT_VERTICES_SUFFIX), target_id)
        self._graph._append_to_lst(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX), source_id)
        self._graph._append_to_lst(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX), target_id)
        # create a key/value for links between source, target and current edge (aimed to be used with indexes)
        self._graph._set(txn, build_key(KIND_EDGE, edge_id, IN_VERTICES_SUFFIX, source_id), 1)
        self._graph._set(txn, build_key(KIND_EDGE, edge_id, OUT_VERTICES_SUFFIX, target_id), 1)
        self._graph._set(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX, source_id), 1)
        self._graph._set(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX, target_id), 1)

    def _remove_denorm_data(self, txn, source, target):
        edge_id = self._entity_id
        source_id = source.get_id()
        target_id = target.get_id()
        # traversal denormalized lists
        self._graph._remove(txn, build_key(KIND_EDGE, edge_id, IN_VERTICES_SUFFIX))
        self._graph._remove(txn, build_key(KIND_EDGE, edge_id, OUT_VERTICES_SUFFIX))
        self._graph._remove(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX))
        self._graph._remove(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX))
        # remove key/value for links between source, target and current edge (aimed to be used with indexes)
        self._graph._remove(txn, build_key(KIND_EDGE, edge_id, IN_VERTICES_SUFFIX, source_id))
        self._graph._remove(txn, build_key(KIND_EDGE, edge_id, OUT_VERTICES_SUFFIX, target_id))
        self._graph._remove(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX, source_id))
        self._graph._remove(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX, target_id))

    def remove(self):
        self._graph._remove_edge(self._entity_id)


class BaseGraph(GraphReadWrite):

    def _prepare_database(self, txn):
        self._set(txn, PREPARED, 1)
        self._set(txn, METADATA_EDGE_COUNTER, 0)
        self._set(txn, METADATA_EDGE_INDEX_COUNTER, 0)
        self._set(txn, METADATA_VERTEX_COUNTER, 0)
        self._set(txn, METADATA_VERTEX_INDEX_COUNTER, 0)

    def _ensure_prepared(self):
        if not(self._has_key(PREPARED)):
            txn = self._transaction_begin()
            try:
                self._prepare_database(txn)
                self._transaction_commit(txn)
            except Exception, e:
                self._transaction_rollback(txn)
                raise GrapheekDataPreparationFailedException(repr(e))

    # Following methods MUST be overriden by child classes :

    def _transaction_begin(self):
        raise NotImplementedError

    def _transaction_commit(self, handle):
        raise NotImplementedError

    def _transaction_rollback(self, handle):
        raise NotImplementedError

    def _has_key(self, key):
        raise NotImplementedError

    def _get(self, txn, key):
        raise NotImplementedError

    def _set(self, key, value):
        raise NotImplementedError

    def _remove(self, key):
        raise NotImplementedError

    def _remove_prefix(self, prefix):
        raise NotImplementedError

    # For next methods, default implementation MAY suffice :
    # BUT overriding them in child classes is a path to performance :)
    # See for instance, kyotocab.KyotoCabinetGraph _init_lst, _get_lst & _append_to_lst overriding

    def _init_lst(self, txn, key):
        # Create an empty list
        self._set(txn, key, [])

    def _get_lst(self, txn, key):
        res = self._get(txn, key)  # if _get returns UNDEFINED, that's also ok, I return it...
        return res

    def _bulk_get_lst(self, txn, keys):
        return [self._get(txn, key) for key in keys]

    def _count_lst(self, txn, key):
        res = self._get_lst(txn, key)
        return 0 if res == UNDEFINED else len(res)

    def _append_to_lst(self, txn, key, value):
        lst = self._get(txn, key)
        if lst == UNDEFINED:
            lst = []
        self._set(txn, key, lst + [value])

    def _remove_from_lst(self, txn, key, value):
        old = self._get(txn, key)
        # Caution : we are only removing ONE occurence
        # This is voluntary
        # For instance, it lst contains neighbour node, we need to remove only one occurence
        # cause current entity and neighbour node can be linked multiple time
        new = old[:]
        new.remove(value)
        self._set(txn, key, new)

    def _update_inc(self, txn, key, value=1):
        oldval_ = self._get(txn, key)
        if oldval_ == UNDEFINED:
            raise GrapheekMissingKeyException
        oldval = int(oldval_)
        newval = oldval + value
        self._set(txn, key, newval)
        return newval

    def _update_dec(self, txn, key, value=1):
        return self._update_inc(txn, key, value * -1)

    def _new_id_for_key(self, txn, key):
        return self._update_inc(txn, key) - 1  # -1 so that entity idx starts at 0

    # Sub data update (no need to override, IMHO)
    # Remark that we are using kind, id instead of key (key is a *key* of the Key Value Store, id is an entity id (node id or edge id for instance))

    def _get_data(self, txn, kind, entity_id):
        key = build_key(kind, entity_id, DATA_SUFFIX)
        res = self._get(txn, key)  # if _get returns UNDEFINED, that's also ok, I return it...
        return res

    def _bulk_update_data(self, _txn, _kind, _entity_id, **updates):
        check_valid_data(updates)
        release_txn = False
        if _txn is None:
            _txn = self._transaction_begin()
            release_txn = True
        try:
            data = self._get_data(_txn, _kind, _entity_id)
            # Remove entity from indexes before updating data (we'll re-add it just after with new values)
            self._remove_from_all_entity_indexes(_txn, _kind, _entity_id, data)
            # Do the update :
            for subkey, value in updates.items():
                key = build_key(_kind, _entity_id, DATA_SUFFIX)
                data[subkey] = value
                self._set(_txn, key, data)
            # Readding entity to indexes :
            self._add_to_all_entity_indexes(_txn, _kind, _entity_id, data)
            if release_txn:
                self._transaction_commit(_txn)
        except Exception, e:
            if release_txn:
                self._transaction_rollback(_txn)
            raise GrapheekDataException(repr(e))

    def _update_data(self, kind, entity_id, subkey, value):
        self._bulk_update_data(None, kind, entity_id, **{subkey: value})  # Don't create a txn, it will be created by _bulk_update_data

    # DON'T OVERRIDE THOSE METHODS :

    def _call_server_script(self, _ctx, _fname, *aliases, **params):
        # 1st, get function from cache :
        func = self._script_cache.get(_fname, None)
        if func is None:
            for module in self._script_module_cache:
                try:
                    func = getattr(module, _fname)
                except AttributeError:
                    pass  # it may not exist in module but may exist in exist...
                if func is not None:
                    # Updating cache and stop iteration
                    self._script_cache[_fname] = func
                    break
        if func is None:
            # not found -> raise an exception to warn user
            raise GrapheekUnknownScriptException('%s method cannot be found' % (_fname,))
        # let's call function :
        return func(self, _ctx, *aliases, **params)

    def _add_node(self, txn, data, node_id=None):
        assert(type(data) == DictType)
        release_txn = False
        if txn is None:
            release_txn = True
            txn = self._transaction_begin()
        try:
            if node_id is None:
                node_id = self._new_id_for_key(txn, METADATA_VERTEX_COUNTER)
            node = Node(node_id, self)
            self._set(txn, build_key(KIND_VERTEX, node_id, DATA_SUFFIX), data)
            node._add_denorm_data(txn)
            # Adding node id to proper node ids list :
            self._append_to_lst(txn, build_key(METADATA_VERTEX_ID_LIST_PREFIX, node_id / ID_LIST_MODULO), node_id)
            # Updating vertex indexes :
            self._add_to_all_entity_indexes(txn, KIND_VERTEX, node_id, data)
            if release_txn:
                self._transaction_commit(txn)
            return node
        except Exception, e:
            if release_txn:
                self._transaction_rollback(txn)
            raise GrapheekDataException(repr(e))

    def _bulk_add_node(self, node_defns, silent=False):
        txn = self._transaction_begin()
        try:
            node_count = len(node_defns)
            last_node_id = self._update_inc(txn, METADATA_VERTEX_COUNTER, node_count) - 1
            first_node_id = last_node_id - node_count + 1
            for node_id, data in zip(range(first_node_id, last_node_id + 1), node_defns):
                self._add_node(txn, data, node_id)
            self._transaction_commit(txn)
            if not(silent):
                res = [Node(node_id, self) for node_id in range(first_node_id, last_node_id + 1)]
                return res
        except Exception, e:
            self._transaction_rollback(txn)
            raise GrapheekDataException(repr(e))

    def _remove_node(self, node_id):
        txn = self._transaction_begin()
        try:
            node = Node(node_id, self)
            # edges attached to this node must be removed before removing any node data
            # (this will infer some denorm data modifications on related outer and inner nodes)
            out_edge_ids = self._get_lst(txn, build_key(KIND_VERTEX, node_id, OUT_EDGES_SUFFIX))
            for out_edge_id in out_edge_ids:
                self._remove_edge(out_edge_id, txn=txn)
            in_edge_ids = self._get_lst(txn, build_key(KIND_VERTEX, node_id, IN_EDGES_SUFFIX))
            for in_edge_id in in_edge_ids:
                self._remove_edge(in_edge_id, txn=txn)
            # now, removing node related data and denorm data :
            node._remove_denorm_data(txn)
            # Removing node id from proper node ids list :
            self._remove_from_lst(txn, build_key(METADATA_VERTEX_ID_LIST_PREFIX, int(node_id) / ID_LIST_MODULO), node_id)
            # Updating vertex indexes before removing data
            data = self._get(txn, build_key(KIND_VERTEX, node_id, DATA_SUFFIX))
            self._remove_from_all_entity_indexes(txn, KIND_VERTEX, node_id, data)
            # Now removing data
            self._remove(txn, build_key(KIND_VERTEX, node_id, DATA_SUFFIX))
            self._transaction_commit(txn)
        except Exception, e:
            self._transaction_rollback(txn)
            raise GrapheekDataException(repr(e))

    def _add_edge(self, txn, source, target, data=None, edge_id=None):
        assert(isinstance(data, DictType))
        release_txn = False
        if txn is None:
            release_txn = True
            txn = self._transaction_begin()
        try:
            if edge_id is None:
                edge_id = self._new_id_for_key(txn, METADATA_EDGE_COUNTER)
            data = data or {}
            # Initializing
            self._init_lst(txn, build_key(KIND_EDGE, edge_id, IN_VERTICES_SUFFIX))
            self._init_lst(txn, build_key(KIND_EDGE, edge_id, OUT_VERTICES_SUFFIX))
            self._init_lst(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX))
            # Persistence and denormalization - START
            self._set(txn, build_key(KIND_EDGE, edge_id, DATA_SUFFIX), data)
            # Adding edge id to proper edge ids list :
            self._append_to_lst(txn, build_key(METADATA_EDGE_ID_LIST_PREFIX, int(edge_id) / ID_LIST_MODULO), edge_id)
            # Edge data denormalization
            edge = Edge(edge_id, self)
            edge._add_denorm_data(txn, source, target)
            # source data denormalization
            source._add_denorm_src_data(txn, target, edge)
            # target data denormalization
            target._add_denorm_tgt_data(txn, source, edge)
            # Updating edge indexes :
            self._add_to_all_entity_indexes(txn, KIND_EDGE, edge_id, data)
            if release_txn:
                self._transaction_commit(txn)
            # Persistence and denormalization - END
            return edge
        except Exception, e:
            if release_txn:
                self._transaction_rollback(txn)
            raise GrapheekDataException(repr(e))

    def _bulk_add_edge(self, edge_defns, silent=False):
        txn = self._transaction_begin()
        edges = []
        try:
            edge_count = len(edge_defns)
            last_edge_id = self._update_inc(txn, METADATA_EDGE_COUNTER, edge_count) - 1
            first_edge_id = last_edge_id - edge_count + 1
            for edge_id, edge_defn in zip(range(first_edge_id, last_edge_id + 1), edge_defns):
                source, target, data = edge_defn
                edges.append(self._add_edge(txn, source, target, data, edge_id=edge_id))
            self._transaction_commit(txn)
            if not(silent):
                res = edges
                return res
        except Exception, e:
            self._transaction_rollback(txn)
            raise GrapheekDataException(repr(e))

    def _bulk_add_edge_by_ids(self, edge_id_defns, silent=False):
        for _, _, data in edge_id_defns:
            check_valid_data(data)
        edge_defns = [(self.v(source_id), self.v(target_id), data) for source_id, target_id, data in edge_id_defns]
        return self._bulk_add_edge(edge_defns, silent)

    def _add_edge_by_ids(self, source_id, target_id, data=None):
        source = Node(source_id, self)
        target = Node(target_id, self)
        return self._add_edge(None, source, target, data)

    def _remove_edge(self, edge_id, txn=None):
        def remove_vertex_denorm_data(txn, node, other, node_suffix):
            rm_denorm_method = node._remove_denorm_src_data if node_suffix == OUT_VERTICES_SUFFIX else node._remove_denorm_tgt_data
            rm_denorm_method(txn, other, edge)
        release_txn = False
        if txn is None:
            release_txn = True
            txn = self._transaction_begin()
        try:
            edge = Edge(edge_id, self)
            source = target = None
            source_id = self._get_lst(txn, build_key(KIND_EDGE, edge_id, IN_VERTICES_SUFFIX))[0]
            source = Node(source_id, self)
            target_id = self._get_lst(txn, build_key(KIND_EDGE, edge_id, OUT_VERTICES_SUFFIX))[0]
            target = Node(target_id, self)
            remove_vertex_denorm_data(txn, source, target, OUT_VERTICES_SUFFIX)
            remove_vertex_denorm_data(txn, target, source, IN_VERTICES_SUFFIX)
            # Removing edge id from proper edge ids list :
            self._remove_from_lst(txn, build_key(METADATA_EDGE_ID_LIST_PREFIX, edge_id / ID_LIST_MODULO), edge_id)
            # Removing edge related lists
            self._remove(txn, build_key(KIND_EDGE, edge_id, IN_VERTICES_SUFFIX))
            self._remove(txn, build_key(KIND_EDGE, edge_id, OUT_VERTICES_SUFFIX))
            self._remove(txn, build_key(KIND_EDGE, edge_id, BOTH_VERTICES_SUFFIX))
            # Updating edge indexes before removing data
            data = self._get(txn, build_key(KIND_EDGE, edge_id, DATA_SUFFIX))
            self._remove_from_all_entity_indexes(txn, KIND_EDGE, edge_id, data)
            # Now removing edge data
            self._remove(txn, build_key(KIND_EDGE, edge_id, DATA_SUFFIX))
            # Removing edge denormalized data
            assert((source or target) is not None)  # Both source and target must NOT be None
            edge._remove_denorm_data(txn, source, target)
            if release_txn:
                self._transaction_commit(txn)
        except Exception, e:
            if release_txn:
                self._transaction_rollback(txn)
            raise GrapheekDataException(repr(e))

    # Traversals given entity ids :

    def _neighbors(self, _kind, _entity_id, _traversal, _cache=None, **filters):
        """
        _neighbors is using a cache (transmitted by iterator) to speed up lookup
        This is done to asymptotically improve performance at the expense of local memory
        Why asymptotically ? because for short path traversal, cache has few probability to be hitted
        On the contrary, for "long path", probability is greater

        WARNING : filter is only used to check if index can be used
        It is not used to really filter neighbors (which is the EntityIterator responsibily)
        Don't be confused by this function signature (I was ... => code needs refactoring)
        """

        indexed_neighbour_ids = None
        use_index = False
        if filters:
            # Do we need to use index ?
            # 1st test(so far) is to find exact matching filters
            # Currently there's no inequality or range indexes...
            exact_filters = _get_exact_filters(**filters)
            indexed_ids_key = _get_indexed_ids_key(self, _kind, exact_filters)
            if indexed_ids_key is not None:
                # Ok, there's a filter, cool, now checking, how many ids are related to this this item
                indexed_count = self._count_lst(None, indexed_ids_key)  # <count> item are indexed and correspond to exact lookups
                # Comparing to number of entities after traversal
                sequential_count = self._get(None, build_key(_kind, _entity_id, _traversal, COUNT_SUFFIX))
                # Finally decide which "strategy" is the best :
                use_index = indexed_count <= sequential_count
            if use_index:
                indexed_neighbour_ids = []
                index_ids = self._get_lst(None, indexed_ids_key)
                for potential_neighbour_id in index_ids:
                    # Is potential_neighbour_id connected to entity_id ? :
                    key = build_key(_kind, _entity_id, _traversal, potential_neighbour_id)
                    if self._has_key(key):
                        indexed_neighbour_ids.append(potential_neighbour_id)
        if indexed_neighbour_ids is not None:
            for neighbour_id in iter(indexed_neighbour_ids):
                yield neighbour_id
        else:
            has_cache = _cache is not None
            lst = None
            if has_cache:
                cache_key = (_kind, _entity_id, _traversal)
                lst = _cache.get(cache_key, None)
            if lst is None:
                key = build_key(_kind, _entity_id, _traversal)
                lst = self._get_lst(None, key)
                if has_cache:
                    _cache[cache_key] = lst
            for entity_id in iter(lst):
                yield entity_id

    # Item id -> Item helper

    def _item_from_id(self, kind, entity_id):
        Klass = Node if kind == KIND_VERTEX else Edge
        return Klass(entity_id, self)

    # Don't override next methods : it's the public interface
    # (or some "private" helper methods for public methods)

    def __X(self, _COUNTER, _KIND, **filters):

        def entity_generator(kind):
            for entity_id in get_kind_ids(self, None, kind):
                yield entity_id

        def indexed_entity_generator(ids):
            for indexed_id in indexed_ids:
                yield indexed_id

        # Try to use index :
        indexed_ids = _get_indexed_ids(self, _KIND, **filters)
        if indexed_ids is not None:
            iterator = indexed_entity_generator(indexed_ids)
        else:
            if filters:
                # If there is some filters, data will be analysed to find occurence
                # So, implicitely, entity existence will be checked
                # <-> no need to check it in iteration
                iterator = entity_generator(_KIND)
            else:
                # No filters -> need to check existence explicitely
                iterator = entity_generator(_KIND)
        return EntityIterator(self, _KIND, filters, iterator)

    def V(self, **filters):
        return self.__X(METADATA_VERTEX_COUNTER, KIND_VERTEX, **filters)

    def E(self, **filters):
        return self.__X(METADATA_EDGE_COUNTER, KIND_EDGE, **filters)

    def v(self, id):
        return Node(id, self)

    def e(self, id):
        return Edge(id, self)

    def add_node(self, **kwargs):
        check_valid_data(kwargs)
        return self._add_node(None, kwargs)

    def bulk_add_node(self, node_defns):
        for data in node_defns:
            check_valid_data(data)
        return self._bulk_add_node(node_defns)

    def add_edge(self, _source, _target, **kwargs):
        check_base_node(_source)
        check_base_node(_target)
        check_valid_data(kwargs)

        return self._add_edge(None, _source, _target, kwargs)

    def bulk_add_edge(self, edge_defns):
        try:
            for source, target, data in edge_defns:
                check_base_node(source)
                check_base_node(target)
                check_valid_data(data)
        except (TypeError, ValueError), e:
            raise GrapheekDataException(repr(e))
        return self._bulk_add_edge(edge_defns)

    def bulk_add_edge_by_ids(self, edge_id_defns):
        return self._bulk_add_edge_by_ids(edge_id_defns)

    def add_edge_by_ids(self, _source_id, _target_id, **kwargs):
        return self._add_edge_by_ids(_source_id, _target_id, kwargs)

    def update_data(self, kind, entity_id, attr, value):
        self._update_data(kind, entity_id, attr, value)

    def _add_to_index(self, txn, kind, index_id, fields, data, entity_id):
        values = [data.get(field, None) for field in fields]
        self._append_to_lst(txn, build_entity_index_values(kind, index_id, *values), entity_id)

    def _remove_from_index(self, txn, kind, index_id, fields, data, entity_id):
        values = [data.get(field, None) for field in fields]
        self._remove_from_lst(txn, build_entity_index_values(kind, index_id, *values), entity_id)

    def __action_on_all_entity_indexes(self, txn, action, kind, entity_id, data):
        if kind == KIND_VERTEX:
            METADATA_INDEX_LIST = METADATA_VERTEX_INDEX_LIST
            METADATA_INDEX_FIELDS_PREFIX = METADATA_VERTEX_INDEX_FIELDS_PREFIX
        elif kind == KIND_EDGE:
            METADATA_INDEX_LIST = METADATA_EDGE_INDEX_LIST
            METADATA_INDEX_FIELDS_PREFIX = METADATA_EDGE_INDEX_FIELDS_PREFIX
        index_lst = self._get_lst(txn, METADATA_INDEX_LIST)
        if index_lst != UNDEFINED:
            for index_id in index_lst:
                fields = self._get(txn, build_key(METADATA_INDEX_FIELDS_PREFIX, index_id))
                action(txn, kind, index_id, fields, data, entity_id)

    def _add_to_all_entity_indexes(self, txn, kind, entity_id, data):
        action = self._add_to_index
        self.__action_on_all_entity_indexes(txn, action, kind, entity_id, data)

    def _remove_from_all_entity_indexes(self, txn, kind, entity_id, data):
        action = self._remove_from_index
        self.__action_on_all_entity_indexes(txn, action, kind, entity_id, data)

    def _add_entity_index(self, kind, *args):
        fields = list(args)
        fields.sort()
        assert(kind in (KIND_VERTEX, KIND_EDGE))
        if kind == KIND_VERTEX:
            METADATA_INDEX_PREFIX = METADATA_VERTEX_INDEX_PREFIX
            METADATA_INDEX_COUNTER = METADATA_VERTEX_INDEX_COUNTER
            METADATA_COUNTER = METADATA_VERTEX_COUNTER
            METADATA_INDEX_LIST = METADATA_VERTEX_INDEX_LIST
            METADATA_INDEX_FIELDS_PREFIX = METADATA_VERTEX_INDEX_FIELDS_PREFIX
        else:
            METADATA_INDEX_PREFIX = METADATA_EDGE_INDEX_PREFIX
            METADATA_INDEX_COUNTER = METADATA_EDGE_INDEX_COUNTER
            METADATA_COUNTER = METADATA_EDGE_COUNTER
            METADATA_INDEX_LIST = METADATA_EDGE_INDEX_LIST
            METADATA_INDEX_FIELDS_PREFIX = METADATA_EDGE_INDEX_FIELDS_PREFIX
        # Checking if index already exists (won't create if it is the case) :
        index_key = '/'.join([METADATA_INDEX_PREFIX] + fields)
        index_id = self._get(None, index_key)
        if index_id != UNDEFINED:
            # Index already exists
            raise GrapheekIndexAlreadyExistsException
        txn = self._transaction_begin()
        try:
            index_id = self._new_id_for_key(txn, METADATA_INDEX_COUNTER)
            self._set(txn, index_key, index_id)
            self._append_to_lst(txn, METADATA_INDEX_LIST, index_id)  # "Registering" index in index list
            self._set(txn, build_key(METADATA_INDEX_FIELDS_PREFIX, index_id), fields)
            entity_count = self._get(txn, METADATA_COUNTER)
            if entity_count == UNDEFINED:
                raise GrapheekDataException
            entity_id = 0
            while entity_id < entity_count:
                data = self._get_data(txn, kind, entity_id)
                if data != UNDEFINED:  # Does not mean that data is None but that key doesn't exist
                    self._add_to_index(txn, kind, index_id, fields, data, entity_id)
                entity_id += 1
            self._transaction_commit(txn)
        except Exception, e:
            self._transaction_rollback(txn)
            raise GrapheekIndexCreationFailedException(repr(e))

    def add_node_index(self, *args):
        self._add_entity_index(KIND_VERTEX, *args)

    def add_edge_index(self, *args):
        self._add_entity_index(KIND_EDGE, *args)

    def _get_entity_indexes(self, kind):
        result = []
        txn = self._transaction_begin()
        try:
            if kind == KIND_VERTEX:
                METADATA_INDEX_COUNTER = METADATA_VERTEX_INDEX_COUNTER
                METADATA_INDEX_FIELDS_PREFIX = METADATA_VERTEX_INDEX_FIELDS_PREFIX
            else:
                METADATA_INDEX_COUNTER = METADATA_EDGE_INDEX_COUNTER
                METADATA_INDEX_FIELDS_PREFIX = METADATA_EDGE_INDEX_FIELDS_PREFIX
            index_count = self._get(txn, METADATA_INDEX_COUNTER)
            for index_id in range(0, index_count):
                fields = self._get(txn, build_key(METADATA_INDEX_FIELDS_PREFIX, index_id))
                result.append(fields)
            self._transaction_commit(txn)
        except Exception, e:
            self._transaction_rollback(txn)
            raise GrapheekDataException(repr(e))
        return result

    def get_node_indexes(self):
        return self._get_entity_indexes(KIND_VERTEX)

    def get_edge_indexes(self):
        return self._get_entity_indexes(KIND_EDGE)

    def _remove_entity_index(self, kind, *args):
        assert(kind in (KIND_VERTEX, KIND_EDGE))
        if kind == KIND_VERTEX:
            METADATA_INDEX_PREFIX = METADATA_VERTEX_INDEX_PREFIX
            METADATA_INDEX_COUNTER = METADATA_VERTEX_INDEX_COUNTER
            METADATA_INDEX_LIST = METADATA_VERTEX_INDEX_LIST
            METADATA_INDEX_FIELDS_PREFIX = METADATA_VERTEX_INDEX_FIELDS_PREFIX
        else:
            METADATA_INDEX_PREFIX = METADATA_EDGE_INDEX_PREFIX
            METADATA_INDEX_COUNTER = METADATA_EDGE_INDEX_COUNTER
            METADATA_INDEX_LIST = METADATA_EDGE_INDEX_LIST
            METADATA_INDEX_FIELDS_PREFIX = METADATA_EDGE_INDEX_FIELDS_PREFIX
        fields = list(args)
        fields.sort()
        # Find index idx :
        index_key = '/'.join([METADATA_INDEX_PREFIX] + fields)
        index_id = self._get(None, index_key)
        if index_id == UNDEFINED:
            raise GrapheekIndexRemovalFailedException
        txn = self._transaction_begin()
        try:
            # Remove key for a given prefix  :
            prefix = build_entity_index_prefix(kind, index_id)
            self._remove_prefix(txn, prefix)
            # Decrement index counter
            self._update_dec(txn, METADATA_INDEX_COUNTER)
            # Remove index key :
            self._remove(txn, index_key)
            # Removing index fields :
            self._remove(txn, build_key(METADATA_INDEX_FIELDS_PREFIX, index_id))
            # Removing index from index list :
            self._remove_from_lst(txn, METADATA_INDEX_LIST, index_id)
            self._transaction_commit(txn)
        except Exception, e:
            self._transaction_rollback(txn)
            raise GrapheekIndexRemovalFailedException(repr(e))

    def remove_node_index(self, *args):
        self._remove_entity_index(KIND_VERTEX, *args)

    def remove_edge_index(self, *args):
        self._remove_entity_index(KIND_EDGE, *args)

    def setup_server_scripts(self, *module_paths):
        import sys
        # Following lines may raise an exception if data module cannot be imported
        # I'm letting exception propagate so that the user can fix path (or other potential errors)
        self._script_module_cache = []
        for module_path in list(module_paths) + ['grapheekdb.server.scripts']:
            if module_path:
                __import__(module_path)
                class_module = sys.modules[module_path]
                self._script_module_cache.append(class_module)
        self._script_cache = {}

