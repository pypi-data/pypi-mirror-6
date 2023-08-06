# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Utilities
# :Creato:    mar 30 set 2008 15:21:56 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

"""
Simple helper functions.
"""

import logging


logger = logging.getLogger(__name__)


def asunicode(s):
    """Force a string to be a unicode instance.

    :param s: any value
    :rtype: str

    If `s` is not already an unicode string, it is assumed it's
    an ``utf-8`` encoded string, a thus converted to unicode and
    returned. Otherwise `s` is returned as is::

      >>> assert asunicode(None) is None
      >>> assert not isinstance(asunicode(b'ascii'), bytes)
    """

    if s is None:
        return None
    elif isinstance(s, bytes):
        return s.decode('utf-8')
    else:
        return str(s)


def normalize(s, title=None):
    """Normalize the case of a string, removing spurious spaces.

    :param s: a string
    :param title: if `True` always titleize the string, if `False`
                  never do that, if `None` (default) only when the
                  input string is all lower case or all upper case
    :rtype: unicode

    ::

      >>> assert normalize(None) is None
      >>> print(normalize('lele gaifax'))
      Lele Gaifax
      >>> print(normalize('LELE'))
      Lele
      >>> print(normalize('LeLe', title=False))
      LeLe
    """

    if s is None:
        return None
    else:
        n = u' '.join(s.strip().split())
        if title != False and (title == True or
                               n == n.upper() or
                               n == n.lower()):
            n = n.title()
        return n


def njoin(elts, stringify=asunicode):
    """Given a sequence of items, concatenate them in a nice way.

    :param elts: a sequence of elements
    :param stringify: the stringification function applied to all elements,
                      by default coerced to `unicode`
    :rtype: unicode

    If `elts` is empty returns an empty unicode string; if it contains
    a single element, returns the stringified element; otherwise
    returns a unicode string composed by all but the last elements
    stringified and joined by a comma, followed by the localized
    version of `and` followed by the last element stringified::

      >>> print(njoin([1,2,3]))
      1, 2 and 3
      >>> print(njoin([1,2]))
      1 and 2
      >>> print(njoin([1]))
      1
      >>> assert njoin([]) == u''
      >>> print(njoin([1,2], stringify=lambda x: str(x*10)))
      10 and 20
    """

    from ..i18n import gettext as _

    elts = [stringify(e) for e in elts if e]
    if not elts:
        return u''
    elif len(elts) == 1:
        return elts[0]
    else:
        last = elts[-1]
        and_ = _(u' and ')
        return u', '.join(elts[:-1]) + and_ + last


def entity_from_primary_key(pkname):
    """Given the name of a primary key, return the mapped entity.

    :param pkname: the name of a primary key
    :rtype: a mapped class
    """

    from sqlalchemy.orm.mapper import _mapper_registry

    for m in list(_mapper_registry):
        if len(m.primary_key) == 1 and m.primary_key[0].name == pkname:
            return m.class_
    raise Exception('Unknown PK: %s' % pkname)


def table_from_primary_key(pkname):
    """Given the name of a primary key, return the related table.

    :param pkname: the name of a primary key
    :rtype: a SQLAlchemy table
    """

    from . import Base

    for t in Base.metadata.sorted_tables:
        if len(t.primary_key.columns) == 1 and pkname in t.primary_key.columns:
            return t
    raise Exception('Unknown PK: %s' % pkname)
