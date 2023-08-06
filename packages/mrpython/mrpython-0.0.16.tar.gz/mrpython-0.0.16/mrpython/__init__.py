# -*- coding: utf-8 -*-


from inspect import (
    getmembers,
    ismethod
)


class TInterface(object):

    _dict_attrs = ()

    def to_dict(self, limit=None):
        m = getmembers(self, lambda x: not ismethod(x))
        m = [i for i in m if not i[0].startswith('_')]
        if limit:
            m = [i for i in m if i[0] in limit]
        else:
            m = [i for i in m if i[0] in self._dict_attrs]
        return dict(m)
