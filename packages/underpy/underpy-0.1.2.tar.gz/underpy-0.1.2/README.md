# UNDERPY

[![Build Status](https://travis-ci.org/ramonski/underpy.png)](https://travis-ci.org/ramonski/underpy)

```
                     _
     _   _ _ __   __| | ___ _ __ _ __  _   _
    | | | | '_ \ / _` |/ _ \ '__| '_ \| | | |
    | |_| | | | | (_| |  __/ |  | |_) | |_| |
     \__,_|_| |_|\__,_|\___|_|  | .__/ \__, |
                                |_|    |___/

functional helpers for python
```


## Functions

``` python
alias(col, mapping)
    Returns a collection of dictionaries with the keys renamed according to
    the mapping

    >>> libraries = [{"isbn": 1, "ed": 1}, {"isbn": 2, "ed": 2}]
    >>> alias(libraries, {"ed": "edition"})
    [{'edition': 1, 'isbn': 1}, {'edition': 2, 'isbn': 2}]

    >>> alias({"a": 1}, {"a": "b"})
    [{'b': 1}]

convert(value, converter)
    Converts a value with a given converter function.

    >>> convert("1", to_int)
    1
    >>> convert("0", to_int)
    0
    >>> convert("a", to_int)

fail(error)
    Raises a RuntimeError with the given error Message

    >>> fail("This failed badly")
    Traceback (most recent call last):
    ...
    RuntimeError: This failed badly

falsy(thing)
    checks if a value is False or None

    >>> falsy(0)
    False
    >>> falsy({})
    False
    >>> falsy([])
    False
    >>> falsy(None)
    True
    >>> falsy(False)
    True

first(lst, n=None)
    get the first element of a list

    >>> lst = [1, 2, 3, 4, 5]
    >>> first(lst)
    1
    >>> first(lst, 3)
    [1, 2, 3]

is_dict(thing)
    checks if an object is a dictionary type

    >>> is_dict({})
    True
    >>> is_dict(dict())
    True
    >>> is_dict("{}")
    False
    >>> is_dict([])
    False

is_digit(thing)
    checks if an object is a digit

    >>> is_digit(1)
    True
    >>> is_digit("1")
    True
    >>> is_digit("a")
    False
    >>> is_digit([])
    False

is_list(thing)
    checks if an object is a list type

    >>> is_list([])
    True
    >>> is_list(list())
    True
    >>> is_list("[]")
    False
    >>> is_list({})
    False

is_string(thing)
    checks if an object is a string/unicode type

    >>> is_string("")
    True
    >>> is_string(u"")
    True
    >>> is_string(str())
    True
    >>> is_string(unicode())
    True
    >>> is_string(1)
    False

is_tuple(thing)
    checks if an object is a tuple type

    >>> is_tuple(())
    True
    >>> is_tuple(tuple())
    True
    >>> is_tuple("()")
    False
    >>> is_tuple([])
    False

omit(dct, *keys)
    Returns a copy of the dictionary filtered to omit the blacklisted keys
    (or list of keys)

    >>> omit({"name": "moe", "age": 50, "userid": "moe1"}, "userid", "age")
    {'name': 'moe'}

pick(dct, *keys)
    Returns a copy of the dictionary filtered to only have values for the
    whitelisted keys (or list of valid keys)

    >>> pick({"name": "moe", "age": 50, "userid": "moe1"}, "name", "age")
    {'age': 50, 'name': 'moe'}

pluck(col, key, default=None)
    Extracts a list of values from a collection of dictionaries

    >>> stooges = [{"name": "moe",   "age": 40},
    ...            {"name": "larry", "age": 50},
    ...            {"name": "curly", "age": 60}]
    >>> pluck(stooges, "name")
    ['moe', 'larry', 'curly']

    It only works with collections

    >>> curly = stooges.pop()
    >>> pluck(curly, "age")
    Traceback (most recent call last):
    ...
    RuntimeError: First argument must be a list or tuple

rename(dct, mapping)
    Rename the keys of a dictionary with the given mapping

    >>> rename({"a": 1, "BBB": 2}, {"a": "AAA"})
    {'AAA': 1, 'BBB': 2}

to_int(thing)
    coverts an object to int

    >>> to_int("0")
    0
    >>> to_int(1)
    1
    >>> to_int("1")
    1
    >>> to_int("a")

to_list(thing)
    converts an object to a list

    >>> to_list(1)
    [1]

    >>> to_list([1,2,3])
    [1, 2, 3]

    >>> to_list(("a", "b", "c"))
    ['a', 'b', 'c']

    >>> to_list(dict(a=1, b=2))
    [{'a': 1, 'b': 2}]

to_string(thing)
    coverts an object to string

    >>> to_string(1)
    '1'
    >>> to_string([])
    '[]'
    >>> to_string(u"a")
    'a'

to_iso_date(thing):
    converts an object to a iso date string

    >>> to_iso_date("")
    ''
    >>> dt = datetime.date.fromtimestamp(1387452665)
    >>> to_iso_date(dt)
    '2013-12-19'

truthy(thing)
    checks if a value is True or not None

    >>> truthy(0)
    True
    >>> truthy({})
    True
    >>> truthy([])
    True
    >>> truthy(None)
    False
    >>> truthy(False)
    False
```


## Running the tests

```
python setup.py nosetests --with-doctest
```


## License

MIT
