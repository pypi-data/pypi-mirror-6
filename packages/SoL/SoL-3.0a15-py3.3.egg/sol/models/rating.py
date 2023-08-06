# -*- coding: utf-8 -*-
# :Progetto:  SoL -- The Rating entity
# :Creato:    gio 05 dic 2013 09:05:58 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

"""
Ratings
-------
"""

from decimal import Decimal
import logging

from sqlalchemy import Column, Index, Sequence, func, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import object_session

from ..i18n import translatable_string as N_
from . import Base, GloballyUnique
from .domains import (
    boolean_t,
    description_t,
    flag_t,
    intid_t,
    prize_t,
    smallint_t,
    volatility_t,
    )

logger = logging.getLogger(__name__)


class Rating(GloballyUnique, Base):
    """A particular rating a tournment can be related to."""

    __tablename__ = 'ratings'

    @declared_attr
    def __table_args__(cls):
        return (GloballyUnique.__table_args__(cls) +
                (Index('%s_uk' % cls.__tablename__,
                       'description',
                       unique=True),))

    ## Columns

    idrating = Column(
        intid_t, Sequence('gen_idrating', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(label=N_('Rating ID'),
                  hint=N_('Unique ID of the rating.')))
    """Primary key."""

    description = Column(
        description_t,
        nullable=False,
        info=dict(label=N_('Rating'),
                  hint=N_('Description of the rating.')))
    """Description of the rating."""

    level = Column(
        flag_t,
        nullable=False,
        info=dict(label=N_('Level'),
                  hint=N_('Rating level.'),
                  dictionary=dict((str(i),v) for i,v in enumerate((
                      N_('Historical (imported) rating'),
                      N_('Level 1, international tourneys'),
                      N_('Level 2, national/open tourneys'),
                      N_('Level 3, regional tourneys'),
                      N_('Level 4, courtyard tourneys'),
                  )))))
    """Rating level."""

    tau = Column(
        prize_t,
        nullable=False,
        default='0.5',
        info=dict(label='Tau',
                  hint=N_('The TAU value for the Glicko2 algorithm.'),
                  min=0.01, max=2))
    """Value of TAU for the Glicko2 algorithm."""

    default_rate = Column(
        smallint_t,
        nullable=False,
        default=1500,
        info=dict(label=N_('Rate'),
                  hint=N_('The default rate value for the Glicko2 algorithm.'),
                  min=1, max=3000))
    """Default value of rate (MU) for the Glicko2 algorithm."""

    default_deviation = Column(
        smallint_t,
        nullable=False,
        default=350,
        info=dict(label=N_('Deviation'),
                  hint=N_('The default deviation value for the Glicko2 algorithm.'),
                  min=1, max=500))
    """Default value of deviation (PHI) for the Glicko2 algorithm."""

    default_volatility = Column(
        volatility_t,
        nullable=False,
        default='0.06',
        info=dict(label=N_('Volatility'),
                  hint=N_('The default volatility value for the Glicko2 algorithm.'),
                  min=0.00001, max=1))
    """Default value of volatility (SIGMA) for the Glicko2 algorithm."""

    inherit = Column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(label=N_('Inherit'),
                  hint=N_('Whether to lookup rates in equal or higher levels ratings.')))
    """Whether to lookup rates in equal or higher levels ratings."""


    ## Relations

    tourneys = relationship('Tourney', backref='rating',
                            passive_updates=False,
                            order_by="Tourney.date",
                            lazy=True)
    """Tourneys using this rating."""

    rates = relationship('Rate', backref='rating',
                         cascade="all, delete-orphan",
                         order_by="Rate.date, Rate.idplayer",
                         lazy=True)
    """List of rates."""

    def getPlayerRating(self, player, before=None):
        """Return the rate of a `player`

        :param player: a Player instance
        :param before: a date instance
        :rtype: an instance of glicko2.Rating

        If `before` is not specified fetch the latest rate, otherwise
        the most recent one preceeding `before`.

        The method considers all ratings at the same level of this one
        or better.
        """

        from . import Rate
        from .glicko2 import Glicko2

        s = object_session(self)

        # Get a list of ratings ids where the level is equal or better
        # than this one

        if self.level > '0' and self.inherit:
            rt = Rating.__table__
            idratings = [r[0] for r in s.execute(
                select([rt.c.idrating]) .where(rt.c.level <= self.level))]
        else:
            idratings = [self.idrating]

        rt = Rate.__table__

        q = select([rt.c.rate, rt.c.deviation, rt.c.volatility]) \
            .where(rt.c.idplayer == player.idplayer)

        if len(idratings) == 1:
            q = q.where(rt.c.idrating == idratings[0])
        else:
            q = q.where(rt.c.idrating.in_(idratings))

        if before is not None:
            q = q.where(rt.c.date < before)

        q = q.order_by(rt.c.date.desc()).limit(1)

        r = s.execute(q).first()

        cr = Glicko2(tau=float(self.tau),
                     mu=self.default_rate,
                     phi=self.default_deviation,
                     sigma=float(self.default_volatility)).create_rating

        return cr(r[0], r[1], r[2]) if r is not None else cr()

    @property
    def ranking(self):
        from . import Player, Rate

        s = object_session(self)

        rt = Rate.__table__
        rta = rt.alias()
        rtc = rt.alias()

        lastrate = select([func.max(rta.c.date)]) \
                   .where(rta.c.idrating == rt.c.idrating) \
                   .where(rta.c.idplayer == rt.c.idplayer)
        ratecount = select([func.count(rtc.c.idrate)]) \
                   .where(rtc.c.idrating == rt.c.idrating) \
                   .where(rtc.c.idplayer == rt.c.idplayer).label('rates_count')
        q = select([rt.c.idplayer,
                    rt.c.rate,
                    rt.c.deviation,
                    rt.c.volatility,
                    ratecount]) \
            .where(rt.c.idrating == self.idrating) \
            .where(rt.c.date == lastrate) \
            .order_by(rt.c.rate.desc())

        rates = s.execute(q).fetchall()

        return [(s.query(Player).get(idplayer), r, rd, rv, rc)
                for idplayer, r, rd, rv, rc in rates]

    @property
    def time_span(self):
        "Return the time span of this rating."

        from . import Rate

        s = object_session(self)

        rt = Rate.__table__

        timespan = select([func.min(rt.c.date), func.max(rt.c.date)]) \
                   .where(rt.c.idrating == self.idrating)
        return s.execute(timespan).first()

    def isPhantom(self, competitor):
        """Determine whether the given competitor is actually a Phantom.

        :param competitor: a Competitor instance

        This is needed because someone use a concrete player as Phantom,
        to customize its name (not everybody have a good sense of humor...)
        """

        return (competitor is None
                or (competitor.points == 0
                    and competitor.totscore == 0
                    and competitor.netscore % 25 == 0))

    def recompute(self, mindate=None, scratch=False):
        """Recompute the whole rating.

        :param mindate: either ``None`` or a date
        :param scratch: a boolean, True to recompute from scratch

        If `mindate` is given, recompute the rating ignoring the tourneys
        *before* that date.
        """

        from collections import defaultdict
        from . import Rate
        from .glicko2 import Glicko2, WIN, LOSS, DRAW

        if self.level == '0' or not self.tourneys:
            return

        firstdate = self.time_span[0]
        if scratch or (firstdate and ((mindate is None and self.tourneys[0].date < firstdate)
                                      or (mindate is not None and mindate < firstdate))):
            logger.debug('Recomputing %r from scratch', self)
            mindate = None
            self.rates = []
        elif mindate:
            rates = self.rates
            while rates and rates[-1].date >= mindate:
                rates.pop()

        s = object_session(self)

        glicko2 = Glicko2(tau=float(self.tau),
                          mu=self.default_rate,
                          phi=self.default_deviation,
                          sigma=float(self.default_volatility))

        rcache = {}
        phantom_p = self.isPhantom

        for tourney in self.tourneys:
            if mindate is not None and tourney.date < mindate:
                continue

            if tourney.championship.playersperteam > 1:
                logger.warning('Cannot update %r for %r: only singles supported, sorry!',
                               self, tourney)
                continue

            if not tourney.prized:
                continue

            outcomes = defaultdict(list)

            for match in tourney.matches:
                c1 = match.competitor1
                c2 = match.competitor2

                # Usually a match against the Phantom is recognizable
                # by the fact that the second competitor is not
                # assigned, but some people insist in using a concrete
                # player to customize the name
                if phantom_p(c1) or phantom_p(c2):
                    # Skip matches against Phantom
                    continue

                occ = outcomes[c1.idplayer1]
                if c2.idplayer1 not in rcache:
                    rcache[c2.idplayer1] = self.getPlayerRating(c2.player1,
                                                                tourney.date)
                occ.append((WIN if match.score1 > match.score2
                            else LOSS if match.score1 < match.score2
                            else DRAW, rcache[c2.idplayer1]))

                occ = outcomes[c2.idplayer1]
                if c1.idplayer1 not in rcache:
                    rcache[c1.idplayer1] = self.getPlayerRating(c1.player1,
                                                                tourney.date)
                occ.append((LOSS if match.score1 > match.score2
                            else WIN if match.score1 < match.score2
                            else DRAW, rcache[c1.idplayer1]))

            # Eventually interpolate the rate of unrated players
            if any(rcache[idplayer].is_default for idplayer in outcomes):
                interpolate_unrated(rcache, tourney.ranking, glicko2, phantom_p)

            for idplayer in outcomes:
                current = rcache[idplayer]
                new = glicko2.rate(current, outcomes[idplayer])

                try:
                    pr = s.query(Rate) \
                          .filter(Rate.idrating == self.idrating) \
                          .filter(Rate.idplayer == idplayer) \
                          .filter(Rate.date == tourney.date).one()
                except NoResultFound:
                    pr = Rate(rating=self,
                              idplayer=idplayer,
                              date=tourney.date)
                    s.add(pr)

                pr.rate = max(new.rate, 800)
                pr.deviation = new.deviation
                pr.volatility = new.volatility

                rcache[idplayer] = new

    def update(self, data, missing_only=False):
        for field in ('tau', 'default_volatility'):
            if field in data and isinstance(data[field], str):
                data[field] = Decimal(data[field])
        return super().update(data, missing_only)

    def serialize(self, serializer):
        "Reduce a single rating to a simple dictionary"

        simple = {}
        simple['guid'] = self.guid
        simple['modified'] = self.modified
        simple['description'] = self.description
        simple['level'] = self.level
        simple['inherit'] = self.inherit
        simple['tau'] = str(self.tau)
        simple['default_rate'] = self.default_rate
        simple['default_deviation'] = self.default_deviation
        simple['default_volatility'] = str(self.default_volatility)

        return simple


def interpolate_unrated(cache, ranking, glicko2, phantom_p):
    """Interpolate the rate of unrated players from the ranking."""

    unrated = []

    sumx = sumy = sumxy = sumx2 = phantoms = 0

    for x, competitor in enumerate(ranking, 1):
        if phantom_p(competitor):
            phantoms += 1
            continue

        if cache[competitor.idplayer1].is_default:
            unrated.append((x, competitor.idplayer1))
        else:
            y = cache[competitor.idplayer1].rate
            sumx += x
            sumy += y
            sumxy += x*y
            sumx2 += x**2

    nrated = len(ranking) - phantoms - len(unrated)
    if nrated < 2:
        # If there are less than 2 rated players, arbitrarily consider
        # two players, the first with 2600pt the other with 1600pt
        nrated = 2
        sumx = 1 + len(ranking) - phantoms
        sumy = 2600 + 1600
        sumxy = 2600 + (len(ranking) - phantoms) * 1600
        sumx2 = 1 + (len(ranking) - phantoms)**2

    den = nrated * sumx2 - sumx**2
    m = float(nrated * sumxy - sumx * sumy) / den
    q = float(sumy * sumx2 - sumx * sumxy) / den

    for x, idplayer in unrated:
        cache[idplayer].update(glicko2.create_rating(mu=int(x * m + q + 0.5)))
