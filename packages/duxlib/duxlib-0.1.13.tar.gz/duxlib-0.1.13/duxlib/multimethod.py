"""
multimethod
===========

Implements multiple dispatch based on a dispatcher function. Think of it as an
extension to instance methods (which dispatch only on their first argument).

Usage
-----

>>> jsonify = multimethod(lambda obj: type(obj))
>>> jsonify.register(   int, lambda o: "I'm an int: %d" % o)
>>> jsonify.register( float, lambda o: "I'm a float: %f" % o)
>>> jsonify.register(   str, lambda o: "I'm a string: %s" % o)
>>> jsonify.register(  dict, lambda o: {k: jsonify(v) for k, v in o.items()})
>>> jsonify.register(  list, lambda o: [jsonify(v) for v in o])

>>> result = jsonify({
...   "a": [1, 2, 3.0],
...   "b": {
...     "ba": ["hello"],
...     "bb": [-1, -2],
...   }
... })

"""

class MultiMethodException(Exception):
  pass


class multimethod(object):
  """Multiple Dispatch"""

  def __init__(self, dispatcher, implementations={}):
    self.implementations = implementations
    self.dispatcher      = dispatcher

  def __call__(self, *args, **kwargs):
    type = self.dispatcher(*args, **kwargs)
    if type in self.implementations:
      return self.implementations[type](*args, **kwargs)
    else:
      raise MultiMethodException("No implementation for '%s'" % (type,))

  def register(self, type, implementation):
    self.implementations[type] = implementation

  def unregister(self, type):
    del self.implementations[type]
