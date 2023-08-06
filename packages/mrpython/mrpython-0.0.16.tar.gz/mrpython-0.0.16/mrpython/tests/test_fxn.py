# -*- coding: utf-8 -*-


import logging

from nose.tools.trivial import assert_equal

from mrpython.fxn import (
    autolog,
    enum,
    ip2long,
    long2ip,
    to_dict,
    walker,
    TInterface
)

from random import (
    choice,
    randint
)


def test_autolog():
    autolog('Testing logger...')
    autolog('Testing warning', logging.WARNING)


def test_enum():
    e = enum(ONE='one', TWO='two')
    assert_equal(e.ONE, 'one')
    assert_equal(e.TWO, 'two')


def test_ip2long():
    ip = '255.255.255.0'
    l = ip2long(ip)
    assert_equal(l, long(4294967040))


def test_long2ip():
    l = long(4294967040)
    ip = long2ip(l)
    assert_equal(ip, '255.255.255.0')


def test_to_dict():
    class TestGuy(object):

        def __init__(self):
            self.name = 'Fred'
            self.age = 12
            self.country = 'USA'

    t = TestGuy()
    r = to_dict(t)
    assert_equal(r, {'country': 'USA', 'age': 12, 'name': 'Fred'})
    r = to_dict(t, limit=('country'))
    assert_equal(r, {'country': 'USA'})


def test_walker():

    class Roots(TInterface):

        _dict_attrs = (
            'trees',
        )

        def __init__(self):
            self.trees = [
                AppleTree(self),
                AppleTree(self),
                AppleTree(self)
            ]

    class AppleTree(TInterface):

        _dict_attrs = (
            'root',
            'apples',
            'water',
            'leaf_count'
        )

        def __init__(self, root):
            self.root = root
            self.apples = [
                Apple(self),
                Apple(self)
            ]
            self.water = choice(waters)
            self.leaf_count = randint(0, 10)

    class Apple(TInterface):

        _dict_attrs = (
            'false_property',
            'mah_property',
            'tree',
            'seeds',
            'water',
            'size'
        )

        @property
        def mah_property(self):
            return 'so proper!'

        @property
        def false_property(self):
            return False

        def __init__(self, tree):
            self.tree = tree
            self.seeds = [AppleSeed(self) for x in xrange(randint(1, 5))]
            self.water = choice(waters)
            self.size = choice(['small', 'medium', 'large'])

    class AppleSeed(TInterface):

        _dict_attrs = (
            'apple',
            'water',
            'potency'
        )

        def __init__(self, apple):
            self.apple = apple
            self.water = choice(waters)
            self.potency = choice(['dull', 'potent', 'juicy'])

    class Water(TInterface):

        _dict_attrs = ('name',)

        def __init__(self, name):
            self.name = name

    waters = [
        Water('ground'),
        Water('rain'),
        Water('bottle')
    ]

    walker(Roots())
