# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Auxiliaries for data schemas.

Things may not work out as you expect when used with non pure data schemas.
"""
from copy import copy
from itertools import izip

from zope.interface import alsoProvides
from zope.interface.interfaces import IMethod


class DataSchemaControlled(object):
  """Base class for classes working with data schemas."""

  # to be overridden by derived classes
  _SCHEMA_ = None # the underlaying schema -- must be pure data (no methods)

  def _fields_(self):
    """the data fields associated with `__SCHEMA__`."""
    return RemoveMethods(self._SCHEMA_)


class SchemaDict(dict, DataSchemaControlled):
  """a dictionary implementing a schema.

  Be careful: methods may hide fields (not checked).
  """

  def __init__(
    self, _mapping_or_iterable_=None, \
    _schema_=None, _unknown_=None, _nodefaults_=False, \
    **kw
    ):
    """initialize the dictionary via *_mapping_or_iterable_* and *kw*.

    *_schema_* overrides `_SCHEMA_`.

    *_unknown_* should either be `None` or a mapping. If it is `None`,
    keys not defined by the associated schema result in a `KeyError`.
    Otherwise, it should be a mapping and unknown items are transfered there.

    *_nodefaults_* indicates that default values should not be provided.
    If it is false, then default values are assigned (if necessary).

    If the object has got all fields defined by the `_SCHEMA_`, then
    is declared to provide *_SCHEMA_*. Note, we do not check that
    the object really conforms to the schema.
    """
    super(SchemaDict, self).__init__(
      *((_mapping_or_iterable_,) if _mapping_or_iterable_ is not None else ()),
      **kw
      )
    if _schema_ is not None: self.__dict__["_SCHEMA_"] = _schema_
    # check conformity
    unknown = {}; schema = self._fields_()
    for k in self.keys():
      if k not in schema:
        unknown[k] = self[k]; del self[k]
    if unknown:
      if _unknown_ is None: raise KeyError(unknown.keys())
      _unknown_.update(unknown)
    # provide default values
    if not _nodefaults_:
      for k in schema:
        if k not in self: self[k] = getattr(schema[k], "default", None)
    # check whether we implement `_SCHEMA_`
    for k in self._SCHEMA_:
      if k not in self: break
    else: alsoProvides(self, self._SCHEMA_)

  def __getattr__(self, k):
    if k in self._fields_(): return self[k]
    raise AttributeError(k)

  def __setattr__(self, k, val):
    target = self if k in self._fields_() else self.__dict__
    target[k] = val

  def copy(self): return copy(self)


class MappingBySchema(DataSchemaControlled):
  """Mixin class to provide a mapping interface for a schema.

  This is in some sense the inverse of `SchemaDict`.
  """

  def iterkeys(self): return iter(self._fields_())
  def itervalues(self): return (self[k] for k in self.iterkeys())
  def iteritems(self): return ((k, self[k]) for k in self.iterkeys())
  def keys(self): return list(self.iterkeys())
  def values(self): return list(self.itervalues())
  def items(self): return list(self.iteritems())
  def __contains__(self, k): return k in self._fields_()
  def update(self, mapping):
    for k, v in mapping.items(): self[k] = v
  def get(self, k, default=None):
    if k not in self: return default
    return getattr(self, k, default)
  def __getitem__(self, k):
    v = self.get(k, self)
    if v is self: raise KeyError(k)
    return v
  def __setitem__(self, k, v):
    if k not in self: raise KeyError(k)
    setattr(self, k, v)
  def __len__(self): return len(tuple(self._fields_()))




def restrict_by_schema(mapping, schema):
  """return a mapping consisting of the items of *mapping* known by *schema*."""
  return dict(i for i in mapping.iteritems() if i[0] in schema)



class RemoveMethods(object):
  """Auxiliary wrapper to filter out methods from a schema."""
  def __init__(self, schema): self.__schema = schema

  def __iter__(self):
    s = self.__schema
    return iter(k for k in s if not IMethod.providedBy(s[k]))

  def get(self, k, default=None):
    v = self.__schema.get(k, self)
    if v is self or IMethod.providedBy(v): return default
    return  v

  def __contains__(self, k):
    return self.get(k, self) is not self

  def __getitem__(self, k):
    v = self.get(k, self)
    if v is self: raise KeyError(k)
    return v

  iterkeys = __iter__
  def itervalues(self): (self[k] for k in self)
  def iteritems(self): izip(self.iterkeys(), self.itervalues)
  def keys(self): return list(self.iterkeys())
  def values(self): return list(self.itervalues())
  def items(self): return list(self.iteritems())
