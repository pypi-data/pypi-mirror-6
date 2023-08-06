# -*- coding: utf-8 -*-


import logging
import inspect
import socket
import struct

from inspect import (
    getmembers,
    ismethod
)


from mrpython import TInterface


def autolog(message=None, level=logging.DEBUG):
    func = inspect.currentframe().f_back.f_code
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    logger = logging.getLogger(module.__name__)
    logger.log(level, '%s: %s' % (func.co_name, message))


def enum(**enums):
    return type('Enum', (), dict(enums.items() + {'items': enums}.items()))


def uberenum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    by_value = dict((value, key) for key, value in enums.iteritems())
    enums['by_value'] = by_value
    return type('Enum', (), enums)


def ip2long(ip):
    packed = socket.inet_aton(ip)
    return long(struct.unpack('!L', packed)[0])


def long2ip(lg):
    return socket.inet_ntoa(struct.pack('!L', lg))


def to_dict(o, limit=None):
    m = getmembers(o, lambda x: not ismethod(x))
    m = [i for i in m if not i[0].startswith('_')]
    if limit:
        m = [i for i in m if i[0] in limit]
    return dict(m)

_traversable_types = (
    dict,
    TInterface
)

_iterable_types = (
    tuple,
    list,
    set
)


def walker(node):
    graph = {}
    paths = {}

    def walk(node, last=None):
        if isinstance(node, _traversable_types):
            node_id = id(node)

            if node_id not in graph:
                graph[node_id] = {}

            if last:
                last_id = id(last)

                if last_id in paths and node_id in paths[last_id]:
                    return u'REC'

                if node_id not in paths:
                    paths[node_id] = []

                paths[node_id].append(last_id)

            if not graph[node_id]:
                kvps = node
                if type(node) is not dict:
                    kvps = node.to_dict()

                d = {}

                for k, v in kvps.iteritems():
                    new_v = walk(v, node)
                    if new_v is u'REC':
                        continue
                    d[k] = new_v
                graph[node_id].update(d)
            return graph[node_id]
        elif isinstance(node, _iterable_types) or hasattr(node, '__iter__'):
            new_l = [walk(x, last) for x in node]
            return list(x for x in new_l if x is not None)
        return node
    return walk(node)
