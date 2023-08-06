# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Field tagging.

Often you would like to provide additional information for your fields -
usually with effects to presentation. Unfortunately, `zope.schema` has
forgotten this use case: it is really hard to give existing fields
additional properties.

Fortunately, `zope.schema` is build on top of `zope.interface` and it
supports so called "tagged values" to add additional information to
its elements. This module uses this feature to provide additional information
for schema elements. As a matter of fact, it works for all schema elements.

Note: If your schemas are used across different packages, ensure the
tag names are sufficiently specific to avoid name clashes, e.g.
by using an appropriate prefix.
"""
from decorator import decorator


class Tagger(object):
  """Auxiliary class to tag `zope.interface` elements based on a prefix."""
  @decorator
  def wrap(f, self, elem, *args, **kw):
    return getattr(self.wrap(elem), f.__name__)(*args, **kw)

  def __init__(self, prefix=''):
    """*prefix* must not contain `:`"""
    self.__prefix = prefix

  @wrap
  def __call__(self, elem, **kw):
    """add *kw* tags to *elem*; return *elem*."""

  @wrap
  def get(self, elem, tag, default=None):
    """return value for *tag* or *default*."""

  @wrap
  def set(self, elem, tag, value):
    """set value of *tag* to *value*."""

  @wrap
  def list(self, elem):
    """list tags defined for *elem*."""

  @wrap
  def contains(self, elem, tag):
    """does *elem* has *tag*."""

  # we override `wrap`
  def wrap(self, elem): return TaggedElement(elem, self.__prefix)


class TaggedElement(object):
  """A `zope.interface.Element` wrapped for easy tagging/tag access."""
  def __init__(self, elem, prefix=''):
    """wrap *elem* for tagging/tag access with *prefix*.

    *prefix* must not contain `:`.
    """
    self.__elem = elem
    assert ":" not in prefix
    if prefix: prefix += ":"
    self.__prefix = prefix

  def __call__(self, **kw):
    """add tags described by *kw*; return the element."""
    elem, prefix = self.__elem, self.__prefix
    for k, v in kw.iteritems(): elem.setTaggedValue(prefix + k, v)
    return elem

  def get(self, tag, default=None):
    elem, prefix = self.__elem, self.__prefix
    r = elem.queryTaggedValue(prefix + tag, default)
    if r is default and type(default) is type(KeyError) and issubclass(default, KeyError): raise default(tag)
    return r

  def __getitem__(self, tag): return self.get(tag, KeyError)

  def set(self, tag, value): self(tag=value)
  def contains(self, tag): return self.get(tag, self) is not self
  __contains__ = contains

  def list(self):
    elem, prefix = self.__elem, self.__prefix
    pl = len(prefix)
    return [t[pl:] for t in elem.getTaggedValueTags() if t.startswith(prefix)]


# the simplest tagger (without prefix)
tag = Tagger().__call__
