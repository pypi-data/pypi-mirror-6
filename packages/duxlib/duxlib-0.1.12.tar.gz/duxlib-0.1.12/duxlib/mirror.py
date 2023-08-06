"""
A class/function decorator that watches input/output of all methods, then
stores it for replay later. In other words, memoize to disk.

```python
from StringIO import StringIO
from duxlib.mirror import Mirror

m  = Mirror("storage.pickle", mode="record")
s  = m(StringIO("I'm a string!"))

s.getvalue()   # "I'm a string!"

m.save()  # happens automatically on program exit

m_ = Mirror("storage.pickle", mode="replay")
s_ = m_(StringIO())   # detect's type

s.getvalue()   # I'm a string!
```
"""
from __future__ import absolute_import

import atexit
import cPickle as pickle
import inspect
import os.path
import signal
import types

from duxlib.collections import hashdict, hashlist


__all__ = ['Mirror']


class Mirror(object):
  """Remember record calls, serialize them to disk for replay on exit or when
  `save()` is called.

  Arguments
  ---------
  path    : string or file-like
      where to save arguments/output
  mode    : "record" or "replay"
  strict  : bool
      if arguments for a method are not cached, throw an Exception.
  exclude : [str]
      don't wrap these method names
  """

  def __init__(self, path, mode='record', strict=False, exclude=[]):
    self.path    = path
    self.mode    = mode
    self.strict  = strict
    self.exclude = exclude

    if mode not in ['record', 'replay']:
      raise Exception("mode must be 'record' or 'replay'; nothing else.")

    self.content = {}
    self.load()
    atexit.register(self.save)

  def _wrap(self, method_id, method):

    def wrapped(*args, **kwargs):
      arguments = serialize_arguments(*args, **kwargs)

      if self.mode == 'record':
        if method_id not in self.content:
          self.content[method_id] = {}
        result = method(*args, **kwargs)
        self.content[method_id][arguments] = result
        return result

      elif self.mode == 'replay':
        if method_id in self.content and arguments in self.content[method_id]:
          return self.content[method_id][arguments]
        else:
          if self.strict:
            raise KeyError("No recorded output for arguments {}".format(arguments))
          else:
            return method(*args, **kwargs)

      else:
        raise Exception("Unknown mode '{}'".format(self.mode))

    return wrapped

  def __call__(self, inst, id=None):
    if id is None:
      id = fullname(inst)

    methods = inspect.getmembers(inst, predicate=inspect.ismethod)
    for method_name, method in methods:
      if method_name in self.exclude:
        continue
      else:
        setattr(
          inst, method_name,
          self._wrap(id + '.' + method_name, method)
        )
    return inst

  def save(self):
    """Save contents to disk"""
    if hasattr(self.path, 'write'):
      pickle.dump(self.content, self.path)
    else:
      with open(self.path, 'wb') as f:
        pickle.dump(self.content, f)

  def load(self):
    """Load contents from disk"""
    if hasattr(self.path, 'read'):
      try:
        self.content = pickle.load(self.path)
      except (EOFError, IOError):
        pass
    elif os.path.exists(self.path):
      with open(self.path, 'rb') as f:
        self.content = pickle.load(f)


_SEPARATOR = "|||"

def serialize_arguments(*args, **kwargs):
  r  = []
  r += args
  r += [_SEPARATOR]
  r += list(sorted(kwargs.items()))
  r  = [sanitize(a) for a in r]
  return tuple(r)


def sanitize(a):
  if isinstance(a, tuple):
    return tuple(sanitize(list(a)))
  if isinstance(a, list):
    return hashlist(sanitize(v) for v in a)
  if isinstance(a, dict):
    return hashdict((sanitize(k), sanitize(v)) for k,v in a.items())
  if isinstance(a, set):
    return frozenset(sanitize(v) for v in a)
  return a


def fullname(o):
  return o.__module__ + '.' + o.__class__.__name__
