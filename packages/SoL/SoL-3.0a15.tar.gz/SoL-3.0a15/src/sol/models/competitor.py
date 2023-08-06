# -*- coding: utf-8 -*-
# :Progetto:  SoL -- The Competitor entity
# :Creato:    gio 27 nov 2008 13:51:08 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

"""
Competitors
-----------
"""

from decimal import Decimal
import logging

from sqlalchemy import Column, ForeignKey, Index, Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ..i18n import translatable_string as N_, gettext as _
from . import Base
from .domains import boolean_t, intid_t, prize_t, smallint_t


logger = logging.getLogger(__name__)


class Competitor(Base):
    """A single competitor in a game.

    A competitor may be a single person or a team of up to four
    players, that participate to a given tourney. On each competitor
    this table keeps the `points`, the `netscore` and his `bucholz`,
    as well as the final `prize`. To disambiguate the ranking it
    maintains also a `totscore`, the total number of pocketed
    carrommen summing up competitor' scores in all played games.
    """

    __tablename__ = 'competitors'

    @declared_attr
    def __table_args__(cls):
        return (Index('%s_uk_1' % cls.__tablename__,
                      'idplayer1', 'idtourney',
                      unique=True),
                Index('%s_uk_2' % cls.__tablename__,
                      'idplayer2', 'idtourney',
                      unique=True),
                Index('%s_uk_3' % cls.__tablename__,
                      'idplayer3', 'idtourney',
                      unique=True),
                Index('%s_uk_4' % cls.__tablename__,
                      'idplayer4', 'idtourney',
                      unique=True))

    ## Columns

    idcompetitor = Column(
        intid_t, Sequence('gen_idcompetitor', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(label=N_('Competitor ID'),
                  hint=N_('Unique ID of the competitor.')))
    """Primary key."""

    idtourney = Column(
        intid_t, ForeignKey('tourneys.idtourney'),
        nullable=False,
        info=dict(label=N_('Tourney ID'),
                  hint=N_('ID of the tourney the competitor belongs to.')))
    """Subscribed tourney's ID."""

    idplayer1 = Column(
        intid_t, ForeignKey('players.idplayer'),
        nullable=False,
        info=dict(label=N_('Player ID'),
                  hint=N_('ID of the player.')))
    """First player's ID."""

    idplayer2 = Column(
        intid_t, ForeignKey('players.idplayer'),
        info=dict(label=N_('2nd player ID'),
                  hint=N_('ID of the second player.')))
    """Second player's ID."""

    idplayer3 = Column(
        intid_t, ForeignKey('players.idplayer'),
        info=dict(label=N_('3rd player ID'),
                  hint=N_('ID of the third player.')))
    """Third player's ID."""

    idplayer4 = Column(
        intid_t, ForeignKey('players.idplayer'),
        info=dict(label=N_('4th player ID'),
                  hint=N_('ID of the fourth player.')))
    """Fourth player's ID."""

    points = Column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(label=N_('Points'),
                  hint=N_('Points of the competitor.')))
    """Points (number of wins * 2 + number of draws)."""

    bucholz = Column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(label=N_('Bucholz'),
                  hint=N_('Weight of the opponents.')))
    """*Weight* of the opponents (sum of opponents' points and netscore)."""

    netscore = Column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(label=N_('Net score'),
                  hint=N_('Net score of all games.')))
    """Net score (sum of carrommen difference in each match)."""

    totscore = Column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(label=N_('Total score'),
                  hint=N_('Total score of all games.')))
    """Total score (sum of carrommen in each match)."""

    prize = Column(
        prize_t,
        nullable=False,
        default=0.0,
        info=dict(label=N_('Final prize'),
                  hint=N_('Final prize assigned at end of tourney.')))
    """Final prize."""

    retired = Column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(label=N_('Retired'),
                  hint=N_('Whether this competitor will play'
                          ' further matches.')))
    """A competitor may stop playing in the middle of the tourney."""

    ## Relations

    player1 = relationship('Player',
                           primaryjoin='Player.idplayer==Competitor.idplayer1',
                           lazy='joined')
    """First player."""

    player2 = relationship('Player',
                           primaryjoin='Player.idplayer==Competitor.idplayer2',
                           lazy='joined')
    """Second player."""

    player3 = relationship('Player',
                           primaryjoin='Player.idplayer==Competitor.idplayer3',
                           lazy='joined')
    """Third player."""

    player4 = relationship('Player',
                           primaryjoin='Player.idplayer==Competitor.idplayer4',
                           lazy='joined')
    """Fourth player."""

    def __repr__(self):
        r = super(Competitor, self).__repr__()
        r = r[:-1] + ': p=%s b=%s ns=%s>' % (self.points,
                                             self.bucholz,
                                             self.netscore)
        return r

    def caption(self, html=None, localized=True):
        "A description of the competitor, made up with the name of each player."

        from .utils import njoin

        if not self.idplayer1:
            return _('Player NOT assigned yet!', just_subst=not localized)
        else:
            captions = [self.player1.caption(html, localized)]
            if self.idplayer2:
                captions.append(self.player2.caption(html, localized))
            if self.idplayer3:
                captions.append(self.player3.caption(html, localized))
            if self.idplayer4:
                captions.append(self.player4.caption(html, localized))
            return njoin(captions, localized=localized)

    description = property(caption)

    @property
    def player1FullName(self):
        return self.idplayer1 and self.player1.description or None

    @property
    def player1Nationality(self):
        return self.idplayer1 and self.player1.nationality or None

    nationality = player1Nationality

    @property
    def player1Sex(self):
        return self.idplayer1 and self.player1.sex or None

    @property
    def player1FirstName(self):
        return self.idplayer1 and self.player1.firstname or None

    @property
    def player1LastName(self):
        return self.idplayer1 and self.player1.lastname or None

    @property
    def player2FullName(self):
        return self.idplayer2 and self.player2.description or None

    @property
    def player2Nationality(self):
        return self.idplayer2 and self.player2.nationality or None

    @property
    def player3FullName(self):
        return self.idplayer3 and self.player3.description or None

    @property
    def player3Nationality(self):
        return self.idplayer3 and self.player3.nationality or None

    @property
    def player4FullName(self):
        return self.idplayer4 and self.player4.description or None

    @property
    def player4Nationality(self):
        return self.idplayer4 and self.player4.nationality or None

    @property
    def rate(self):
        if not self.tourney.idrating:
            return 0

        rating = self.tourney.rating
        date = self.tourney.date
        total = 0

        if self.idplayer1:
            rate = rating.getPlayerRating(self.player1, date)
            if rate is not None:
                total = rate.mu

            if self.idplayer2:
                rate = rating.getPlayerRating(self.player2, date)
                if rate is not None:
                    total += rate.mu

                if self.idplayer3:
                    rate = rating.getPlayerRating(self.player3, date)
                    if rate is not None:
                        total += rate.mu

                    if self.idplayer4:
                        rate = rating.getPlayerRating(self.player4, date)
                        if rate is not None:
                            total += rate.mu

        return total

    def update(self, data, missing_only=False):
        if 'prize' in data and isinstance(data['prize'], str):
            data['prize'] = Decimal(data['prize'])
        return super().update(data, missing_only)

    def serialize(self, serializer):
        "Reduce a single competitor to a simple dictionary"

        simple = {}
        pers = simple['players'] = []
        if self.idplayer1:
            pers.append(serializer.addPlayer(self.player1))
        if self.idplayer2:
            pers.append(serializer.addPlayer(self.player2))
        if self.idplayer3:
            pers.append(serializer.addPlayer(self.player3))
        if self.idplayer4:
            pers.append(serializer.addPlayer(self.player4))
        if self.points:
            simple['points'] = self.points
        if self.netscore:
            simple['netscore'] = self.netscore
        if self.totscore:
            simple['totscore'] = self.totscore
        if self.bucholz:
            simple['bucholz'] = self.bucholz
        if self.prize:
            simple['prize'] = str(self.prize)
        if self.retired:
            simple['retired'] = self.retired

        return simple
