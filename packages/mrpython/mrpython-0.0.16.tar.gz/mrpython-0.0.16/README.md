# Mr. Python
[![Build Status](https://travis-ci.org/petermelias/mrpython.png?branch=master)](https://travis-ci.org/petermelias/mrpython) [![Coverage Status](https://coveralls.io/repos/petermelias/mrpython/badge.png?branch=master)](https://coveralls.io/r/petermelias/mrpython?branch=master) [![Downloads](https://pypip.in/d/mrpython/badge.png)](https://pypi.python.org/pypi/mrpython/) [![Downloads](https://pypip.in/v/mrpython/badge.png)](https://pypi.python.org/pypi/mrpython/)

A collection of functions, decorators and data that don't seem to fit into any of my (or anybody else's) libraries.

## Functions
* ``` autolog(message, level=logging.DEBUG) ```
* ``` enum(**enums) ```
* ``` ip2long(ip) ```
* ``` long2ip(long) ```
* ``` to_dict(o, limit=None) ```
* ``` walker(node, limit=None) ```

## Data
* STATES (dict)
* ORDERED_STATES (OrderedDict)

## Interfaces
* TInterface (only for use with walker)


### Instructions for using walker

1. Inherit your walkable nodes from ``` mrpython.TInterface ```
2. Set the ``` _dict_attrs attribute on all of your nodes to limit the extent to which they walk
3. Pass one of the nodes to ``` walker(node) ```
4. Store the resulting dictionary.

If you want to override the ``` _dict_attrs ``` default limiting, call the ``` to_dict ``` method on your starting node and supply the ``` limit ``` parameter and then pass the resulting dictionary to the ``` walker(node) ``` function.