# -*- coding: utf-8 -*-
# :Progetto:  SoL -- The PlayerRating entity
# :Creato:    ven 06 dic 2013 19:20:58 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

"""
Rates
-----
"""

from decimal import Decimal
import logging

from sqlalchemy import Column, ForeignKey, Index, Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ..i18n import translatable_string as N_, gettext as _
from . import Base
from .domains import date_t, intid_t, int_t, volatility_t


logger = logging.getLogger(__name__)


class Rate(Base):
    """The Glicko rating of a player."""

    __tablename__ = 'rates'

    @declared_attr
    def __table_args__(cls):
        return (Index('%s_uk' % cls.__tablename__,
                      'idrating', 'idplayer', 'date',
                      unique=True),)

    ## Columns

    idrate = Column(
        intid_t, Sequence('gen_idrate', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(label=N_(u'Player rate ID'),
                  hint=N_(u'Unique ID of the player rate.')))
    """Primary key."""

    idrating = Column(
        intid_t, ForeignKey('ratings.idrating'),
        nullable=False,
        info=dict(label=N_(u'Rating ID'),
                  hint=N_(u'ID of the related rating.')))
    """Related rating's ID."""

    idplayer = Column(
        intid_t, ForeignKey('players.idplayer'),
        nullable=False,
        info=dict(label=N_(u'Player ID'),
                  hint=N_(u'ID of the related player.')))
    """Related player's ID."""

    date = Column(
        date_t,
        nullable=False,
        info=dict(label=N_(u'Date'),
                  hint=N_(u'Date of the rating.')))
    """Rating date."""

    rate = Column(
        int_t,
        nullable=False,
        info=dict(label=N_(u'Rate'),
                  hint=N_(u'The value of Glicko rate.')))
    """The value of Glicko rating."""

    deviation = Column(
        int_t,
        nullable=False,
        info=dict(label=N_(u'Deviation'),
                  hint=N_(u'The value of Glicko deviation.')))
    """The value of Glicko deviation."""

    volatility = Column(
        volatility_t,
        nullable=False,
        info=dict(label=N_(u'Volatility'),
                  hint=N_(u'The value of the Glicko volatility.')))

    ## Relations

    player = relationship('Player')
    """The related player."""

    def __repr__(self):
        r = super(Rate, self).__repr__()
        r = r[:-1] + ': r=%s d=%s v=%s>' % (self.rate,
                                            self.deviation,
                                            self.volatility)
        return r

    def caption(self, html=None):
        "A description of the rate."

        format = N_(u'$player in $rating on $date')
        return _(format, mapping=dict(
            player=self.player.caption(html),
            rating=self.rating.caption(html),
            date=self.date.strftime(_(u'%m-%d-%Y'))))

    def update(self, data):
        if 'volatility' in data:
            data['volatility'] = Decimal(data['volatility'])
        super().update(data)

    def serialize(self, serializer):
        "Reduce a single rate to a simple dictionary"

        simple = {}
        simple['rating'] = serializer.addRating(self.rating)
        simple['player'] = serializer.addPlayer(self.player)
        simple['date'] = self.date
        simple['rate'] = self.rate
        simple['deviation'] = self.deviation
        simple['volatility'] = str(self.volatility)

        return simple
