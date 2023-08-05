# -*- coding:utf-8 -*-

from types import BooleanType, DictType, FloatType, IntType
from types import ListType, LongType, NoneType, StringType, TupleType, UnicodeType

import zmq.green as zmq
try:
    import ujson as json
except ImportError:  # pragma : no cover
    import json

from grapheekdb.backends.data.keys import KIND_VERTEX, KIND_EDGE

from grapheekdb.lib.validations import check_valid_data

from grapheekdb.lib.readwrite import GraphReadWrite

from grapheekdb.lib.exceptions import GrapheekException
from grapheekdb.lib.exceptions import GrapheekDataException
from grapheekdb.lib.exceptions import GrapheekUnmarshallingException
from grapheekdb.lib.exceptions import GrapheekInvalidDataTypeException


def unmarshall(graph, item):
    if isinstance(item, (BooleanType, FloatType, IntType, LongType, NoneType, StringType, UnicodeType)):
        return item
    if isinstance(item, (ProxyNode, ProxyEdge)):
        return item
    elif isinstance(item, DictType):
        # Check if item is in fact a "special" dict (<-> handling an instance serialization)
        kind = item.get('__', None)
        if kind is not None:
            # If msg is an exception, raise it rapidly (do no count an caller to raise sth)
            # (But this doesn't forbid caller to catch exception, btw)
            if kind == 'x':
                raise GrapheekException(
                    '\n____________________________________\n*** SERVER *** exception traceback :\n%s'
                    % (item['d'],)
                )
            elif kind == 'n':
                return ProxyNode(graph, item['_i'], **unmarshall(graph, item['d']))
            elif kind == 'e':
                return ProxyEdge(graph, item['_i'], **unmarshall(graph, item['d']))
            elif kind == 'd':
                return dict((unmarshall(graph, key), unmarshall(graph, value)) for key, value in item['d'])
        else:
            items = [(unmarshall(graph, key), unmarshall(graph, value)) for key, value in item.items()]
            return dict(items)
    elif isinstance(item, (ListType, TupleType)):
        return [unmarshall(graph, x) for x in item]
    raise GrapheekUnmarshallingException('Unknown type %s' % type(item))


def check_proxy_node(entity):
    if not(isinstance(entity, ProxyNode)):
        raise GrapheekInvalidDataTypeException('%s is not a node')


class ProxyDotExport(object):

    def __init__(self, dotstring):
        self._dotstring = dotstring

    def __repr__(self):
        return self._dotstring

    def to_dot(self):
        return self._dotstring


class ProxyEntityIterator(object):

    def __init__(self, graph, commands):
        self._graph = graph
        self._commands = commands
        self._current_iteration = None

    def _request(self):
        return self._graph._request(self._commands)

    def __iter__(self):
        return self

    def next(self):
        if self._current_iteration is None:
            response = self._request()
            self._current_iteration = iter(response)
        try:
            return self._current_iteration.next()
        except StopIteration:
            self._current_iteration = None
        raise StopIteration

    def _do(self, _method, *args, **kwargs):
        command = [_method, args, kwargs]
        return ProxyEntityIterator(self._graph, self._commands + [command])

    def _raw(self, _method, *args, **kwargs):
        command = [_method, args, kwargs]
        response = self._graph._request(self._commands + [command])
        return unmarshall(self._graph, response)

    def _jump(self, _traversal, *args, **kwargs):
        return self._do(_traversal, *args, **kwargs)

    def inV(self, *args, **kwargs):
        return self._jump('inV', *args, **kwargs)

    def outV(self, *args, **kwargs):
        return self._jump('outV', *args, **kwargs)

    def bothV(self, *args, **kwargs):
        return self._jump('bothV', *args, **kwargs)

    def IN(self, *args, **kwargs):
        return self._jump('IN', *args, **kwargs)

    def OUT(self, *args, **kwargs):
        return self._jump('OUT', *args, **kwargs)

    def BOTH(self, *args, **kwargs):
        return self._jump('BOTH', *args, **kwargs)

    def inE(self, **kwargs):
        # TODO : Check that the "ring" on which we are is composed of nodes (NOT edges)
        return self._jump('inE', **kwargs)

    def outE(self, **kwargs):
        # TODO : Check that the "ring" on which we are is composed of nodes (NOT edges)
        return self._jump('outE', **kwargs)

    def bothE(self, **kwargs):
        # TODO : Check that the "ring" on which we are is composed of nodes (NOT edges)
        return self._jump('bothE', **kwargs)

    def dedup(self):
        return self._do('dedup')

    def data(self):
        return self._raw('data')

    def limit(self, count):
        return self._do('limit', count)

    def aka(self, alias):
        return self._do('aka', alias)

    def count(self):
        return int(self._raw('count'))

    def remove(self):
        self._raw('remove')

    def update(self, **updates):
        self._raw('update', **updates)

    def collect(self, *args):
        return self._raw('collect', *args)

    def agg(self, aggtype='+', asc=False):
        return self._raw('agg', aggtype, asc)

    def call(self, _fname, *aliases, **params):
        return self._raw('call', _fname, *aliases, **params)

    def request(self, _fname, *aliases, **params):
        return self._raw('request', _fname, *aliases, **params)

    def dot(self, node_label=None, edge_label=None, limit=100):
        dotstring = self._raw('_dot_str', node_label, edge_label, limit)
        return ProxyDotExport(dotstring)


class ProxyEntity(object):

    def __init__(self, _graph, _entity_id, **data):
        check_valid_data(data)
        self._entity_id = _entity_id
        self._graph = _graph
        self._commands = [[self._kind, [_entity_id], {}]]
        self._data = data

    def __repr__(self):
        kind = 'node' if self._kind == KIND_VERTEX else 'edge'
        return '<%s id:%s data:%s>' % (kind, self._entity_id, repr(self._data))

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other.get_id() == self.get_id() and other._graph == self._graph

    def __ne__(self, other):
        # Cf Python Doc : http://docs.python.org/2/reference/datamodel.html#object.__ne__
        # "When defining __eq__(), one should also define __ne__() so that the operators will behave as expected"
        return not self.__eq__(other)

    def __getattr__(self, attr):
        # Get value form local data
        if attr in self._data:
            return self._data[attr]
        # Try to update data :
        data = self._data = self.data()
        try:
            return data[attr]
        except KeyError:
            raise AttributeError("%r instance has no attribute %r" % (self.__class__, attr))

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            self.__dict__.update({attr: value})
        else:
            command = ['update_data', [self._kind, self._entity_id, attr, value], {}]
            self._graph._request([command])

    def _do(self, _method, *args, **kwargs):
        command = [_method, args, kwargs]
        return ProxyEntityIterator(self._graph, self._commands + [command])

    def _raw(self, _method, *args, **kwargs):
        command = [_method, args, kwargs]
        response = self._graph._request(self._commands + [command])
        return unmarshall(self._graph, response)

    def inV(self, *args, **kwargs):
        return self._do('inV', *args, **kwargs)

    def outV(self, *args, **kwargs):
        return self._do('outV', *args, **kwargs)

    def bothV(self, *args, **kwargs):
        return self._do('bothV', *args, **kwargs)

    def IN(self, *args, **kwargs):
        return self._do('IN', *args, **kwargs)

    def OUT(self, *args, **kwargs):
        return self._do('OUT', *args, **kwargs)

    def BOTH(self, *args, **kwargs):
        return self._do('BOTH', *args, **kwargs)

    def data(self):
        return self._data or self._raw('data')

    def get_id(self):
        return int(self._entity_id)

    def remove(self):
        return self._raw('remove')

    def update(self, **updates):
        self._raw('update', **updates)
        # No exception raised -> Apply updates on self.__dict__
        self.__dict__.update(updates)

    def aka(self, alias):
        return self._do('aka', alias)


class ProxyNode(ProxyEntity):

    def __init__(self, _graph, _node_id, **data):
        self._kind = KIND_VERTEX
        super(ProxyNode, self).__init__(_graph, _node_id, **data)

    def inE(self, **kwargs):
        return self._do('inE', **kwargs)

    def outE(self, **kwargs):
        return self._do('outE', **kwargs)

    def bothE(self, **kwargs):
        return self._do('bothE', **kwargs)


class ProxyEdge(ProxyEntity):

    def __init__(self, _graph, _edge_id, **data):
        self._kind = KIND_EDGE
        super(ProxyEdge, self).__init__(_graph, _edge_id, **data)


class ProxyGraph(GraphReadWrite):

    def __init__(self, address):  # pragma : no cover
        self._address = address
        self._zmq_context = zmq.Context()
        self._zmq_socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect(address)

    def _request(self, commands):
        data = json.dumps(commands)
        self._zmq_socket.send(data)
        raw = self._zmq_socket.recv()
        msg = json.loads(raw)
        return unmarshall(self, msg)

    def v(self, entity_id):
        return ProxyNode(self, entity_id)

    def V(self, **kwargs):
        command = [KIND_VERTEX.upper(), [], kwargs]
        return ProxyEntityIterator(self, [command])

    def e(self, entity_id):
        return ProxyEdge(self, entity_id)

    def E(self, **kwargs):
        command = [KIND_EDGE.upper(), [], kwargs]
        return ProxyEntityIterator(self, [command])

    def add_node(self, **kwargs):
        check_valid_data(kwargs)
        command = ['add_node', [], kwargs]
        return self._request([command])

    def bulk_add_node(self, node_defns):
        for data in node_defns:
            check_valid_data(data)
        command = ['bulk_add_node', [node_defns], {}]
        return self._request([command])

    def add_edge(self, _source, _target, **kwargs):
        check_valid_data(kwargs)
        check_proxy_node(_source)
        check_proxy_node(_target)
        source_id = _source.get_id()
        target_id = _target.get_id()
        command = ['add_edge_by_ids', [source_id, target_id], kwargs]
        return self._request([command])

    def bulk_add_edge(self, edge_defns):
        try:
            for source, target, data in edge_defns:
                check_proxy_node(source)
                check_proxy_node(target)
                check_valid_data(data)
        except (TypeError, ValueError), e:
            raise GrapheekDataException(repr(e))
        # Don't be suprised by [[ ... ]] instead of [ ... ]
        # Server function is expecting only one argument :
        args = [[(source.get_id(), target.get_id(), data) for source, target, data in edge_defns]]
        command = ['bulk_add_edge_by_ids', args, {}]
        return self._request([command])

    def _add_entity_index(self, kind, *args):
        assert(kind in (KIND_EDGE, KIND_VERTEX))
        command = ['add_node_index' if kind == KIND_VERTEX else 'add_edge_index', args, {}]
        return self._request([command])

    def add_node_index(self, *args):
        return self._add_entity_index(KIND_VERTEX, *args)

    def add_edge_index(self, *args):
        return self._add_entity_index(KIND_EDGE, *args)

    def _get_entity_indexes(self, kind):
        assert(kind in (KIND_EDGE, KIND_VERTEX))
        command = ['_get_entity_indexes', [kind], {}]
        return self._request([command])

    def get_node_indexes(self):
        return self._get_entity_indexes(KIND_VERTEX)

    def get_edge_indexes(self):
        return self._get_entity_indexes(KIND_EDGE)

    def _remove_entity_index(self, kind, *args):
        assert(kind in (KIND_EDGE, KIND_VERTEX))
        command = ['remove_node_index' if kind == KIND_VERTEX else 'remove_edge_index', args, {}]
        return self._request([command])

    def remove_node_index(self, *args):
        return self._remove_entity_index(KIND_VERTEX, *args)

    def remove_edge_index(self, *args):
        return self._remove_entity_index(KIND_EDGE, *args)
