from __future__ import absolute_import

import itertools


class DuxlibException(Exception):
  pass


def and_then(*args):
  if len(args) == 1 and isinstance(args[0], list):
    args = args[0]

  if not len(args) > 0:
    raise DuxlibException("and_then requires > 1 functions")

  def decorated(*args_, **kwargs_):
    result = args[0](*args_, **kwargs_)
    for f in args[1:]:
      result = f(result)
    return result

  return decorated


def combinations(d):
  """
  Cartesian product of values in a dict

  {
    "a": [1,2],
    "b": [2,3]
  }

  becomes

  [
    {"a": 1, "b": 2},
    {"a": 1, "b": 3},
    {"a": 2, "b": 2},
    {"a": 2, "b": 3},
  ]
  """
  if len(d) > 0:
    keys, values = zip(*d.items())
    return [
      dict(zip(keys, v)) for v in itertools.product(*values)
    ]
  else:
    return []
