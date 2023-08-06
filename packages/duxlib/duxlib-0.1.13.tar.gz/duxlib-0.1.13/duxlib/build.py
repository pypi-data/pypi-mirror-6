from __future__ import absolute_import


def subclasses(cls):
  """Get all subclasses of a given `cls`"""
  result = {c.__name__:c for c in cls.__subclasses__()}
  for subclass in result.values():
    result.update(subclasses(subclass))
  return result


class BuildException(Exception):
  pass


class Buildable(object):

  @classmethod
  def build(cls, config):
    """
    Default build method for an abstract class defers to concrete
    implementations

    Parameters
    ----------
    config : attribute dict
        configuration parameters.
    """
    types = subclasses(cls)
    if len(types) == 0:
      raise BuildException("No subclasses of type {}".format(cls.__name__))
    elif 'type' not in config:
      raise BuildException("`type` parameter not specified in `config`")
    elif config['type'] not in types:
      raise BuildException("{} isn't one of {}'s subtypes".format(config.type, cls.__name__))
    else:
      return types[config['type']].build(config)

