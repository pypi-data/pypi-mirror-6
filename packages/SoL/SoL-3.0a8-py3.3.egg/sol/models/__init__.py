# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Business objects
# :Creato:    sab 27 set 2008 14:00:47 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

"""The application's model objects"""

from uuid import uuid1

from sqlalchemy import Column, Index, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import object_session, scoped_session, sessionmaker

import zope.sqlalchemy

from ..i18n import translatable_string as N_
from .domains import guid_t, timestamp_t


class AbstractBase(object):
    "Abstract base entity class."

    @classmethod
    def check_insert(klass, session, fields):
        "Perform any check before an new instance is inserted"

    def check_update(self, fields):
        "Perform any check before updating the instance"

    def delete(self):
        "Delete this instance from the database."

        object_session(self).delete(self)

    def update(self, data):
        "Update entity with given data."

        self.check_update(data)

        for attr in data:
            if hasattr(self, attr):
                setattr(self, attr, data[attr])

    def __str__(self):
        "Return a description of the entity."

        return self.caption(html=False)

    def __repr__(self):
        "Return an ASCII representation of the entity."

        return '<%s "%s">' % (
            self.__class__.__name__,
            str(self).encode('ascii', 'replace').decode('ascii'))

    def caption(self, html=None):
        """Return an Unicode, possibly HTML-decorated, caption of the entity.

        :param html: either ``None`` (the default) or a boolean value

        If `html` is ``None`` or ``True`` then the result may be an
        HTML representation of the entity, otherwise it is plain text.
        """

        return self.description


class GloballyUnique(object):
    "Mixin class for globally unique identified entities."

    _guid = Column(
        guid_t, name="guid",
        nullable=False,
        default=lambda: uuid1().hex,
        info=dict(label=N_(u'GUID'),
                  hint=N_(u'The globally unique identifier of the record.'),
                  hidden=True,
                  sortable=False))
    """An UUID key."""

    modified = Column(
        timestamp_t,
        nullable=False,
        server_default=func.now(),
        info=dict(label=N_(u'Modified'),
                  hint=N_(u'Timestamp of the last change to the record.'),
                  hidden=True))
    """Last update timestamp."""

    @hybrid_property
    def guid(self):
        "A global unique identifier for this entity."
        return self._guid

    @guid.setter
    def guid(self, guid):
        if self._guid:
            if self._guid != guid:
                raise ValueError('Cannot update instance guid')
        else:
            self._guid = guid

    @staticmethod
    def __table_args__(cls):
        # Put these fields near the end of the table, when creating it
        # from scratch
        if cls._guid._creation_order < 1000:
            cls._guid._creation_order = 1000
            cls.modified._creation_order = 1001

        return (Index('%s_guid' % cls.__tablename__.lower(), 'guid',
                      unique=True),)


DBSession = scoped_session(sessionmaker())
"The global SA session maker"

zope.sqlalchemy.register(DBSession)

Base = declarative_base(cls=AbstractBase)
"The common parent class for all declarative mapped classed."


from .championship import Championship
from .club import Club
from .competitor import Competitor
from .match import Match
from .mergedplayer import MergedPlayer
from .player import Player
from .rate import Rate
from .rating import Rating
from .tourney import Tourney


def wipe_database():
    """Delete all records in all tables."""

    import transaction
    from zope.sqlalchemy import mark_changed

    s = DBSession()

    with transaction.manager:
        s.execute(MergedPlayer.__table__.delete())
        s.execute(Match.__table__.delete())
        s.execute(Competitor.__table__.delete())
        s.execute(Rate.__table__.delete())
        s.execute(Player.__table__.delete())
        s.execute(Tourney.__table__.delete())
        s.execute(Rating.__table__.delete())
        s.execute(Championship.__table__.delete())
        s.execute(Club.__table__.delete())
        mark_changed(s)
