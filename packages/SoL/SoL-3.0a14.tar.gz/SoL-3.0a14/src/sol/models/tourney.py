# -*- coding: utf-8 -*-
# :Progetto:  SoL -- The Tourney entity
# :Creato:    gio 27 nov 2008 13:54:14 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

"""
Tourneys
--------
"""

import logging

from sqlalchemy import Column, ForeignKey, Index, Sequence, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import object_session, relationship

from ..i18n import translatable_string as N_, gettext as _
from . import Base, GloballyUnique
from .domains import (
    boolean_t,
    code_t,
    date_t,
    description_t,
    intid_t,
    smallint_t,
    )
from .errors import OperationAborted


logger = logging.getLogger(__name__)


class Tourney(GloballyUnique, Base):
    """A single tournment."""

    __tablename__ = 'tourneys'

    @declared_attr
    def __table_args__(cls):
        return (GloballyUnique.__table_args__(cls) +
                (Index('%s_uk' % cls.__tablename__,
                       'date', 'idchampionship',
                       unique=True),))

    ## Columns

    idtourney = Column(
        intid_t, Sequence('gen_idtourney', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(label=N_('Tourney ID'),
                  hint=N_('Unique ID of the tourney.')))
    """Primary key."""

    idchampionship = Column(
        intid_t, ForeignKey('championships.idchampionship'),
        nullable=False,
        info=dict(label=N_('Championship ID'),
                  hint=N_('ID of the championship the tourney belongs to.')))
    """Related championship's ID."""

    idrating = Column(
        intid_t, ForeignKey('ratings.idrating'),
        info=dict(label=N_('Rating ID'),
                  hint=N_('ID of the rating this tourney uses.')))
    """Possible rating ID this tourney uses and updates."""

    date = Column(
        date_t,
        nullable=False,
        info=dict(label=N_('Date'),
                  hint=N_('Date of the event.')))
    """Event date."""

    description = Column(
        description_t,
        nullable=False,
        info=dict(label=N_('Tourney'),
                  hint=N_('Description of the tourney.')))
    """Event description."""

    location = Column(
        description_t,
        info=dict(label=N_('Location'),
                  hint=N_('Location of the tourney.')))
    """Event location."""

    duration = Column(
        smallint_t,
        nullable=False,
        default=45,
        info=dict(label=N_('Duration'),
                  hint=N_('Duration in minutes of each turn.'),
                  min=0))
    """Duration in minutes of each turn, used by the clock."""

    prealarm = Column(
        smallint_t,
        nullable=False,
        default=5,
        info=dict(label=N_('Prealarm'),
                  hint=N_('Prealarm before the end of the turn, usually no more games'
                          ' after that.'),
                  min=0))
    """Prealarm before the end of the turn."""

    couplings = Column(
        code_t,
        nullable=False,
        default='serial',
        info=dict(label=N_(u'Pairing method'),
                  hint=N_('Method used to couple competitors at each turn.'),
                  dictionary=dict(serial=N_('Ranking order'),
                                  dazed=N_('Cross ranking order'))))
    """Kind of coupling used to build next turn. It may be `serial` or `dazed`."""

    currentturn = Column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(label=N_('Current turn'),
                  hint=N_('Current turn number.')))
    """The current turn."""

    rankedturn = Column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(label=N_('Ranked turn'),
                  hint=N_('To which turn the ranking is up-to-date with.')))
    """The highest turn considered in the ranking."""

    prized = Column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(label=N_('Prized'),
                  hint=N_('Whether the final prizes has been assigned.')))
    """Whether the tourney is closed, and final prizes updated."""

    ## Relations

    competitors = relationship('Competitor', backref='tourney',
                               cascade="all, delete-orphan",
                               lazy='joined')
    """List of competitors."""

    matches = relationship('Match', backref='tourney',
                           cascade="all, delete-orphan",
                           order_by="Match.turn, Match.board",
                           lazy=True)
    """List of matches, sorted by turn and board."""

    def caption(self, html=None, localized=True):
        return _('$tourney — $championship, $date',
                 just_subst=not localized, mapping=dict(
                     tourney=self.description,
                     championship=self.championship.caption(html, localized),
                     date=self.date.strftime(_('%m-%d-%Y'))))

    def allPlayers(self):
        "Generator that return all involved players."

        for c in self.competitors:
            yield c.player1
            if c.player2 is not None:
                yield c.player2
                if c.player3 is not None:
                    yield c.player3
                    if c.player4 is not None:
                        yield c.player4

    @property
    def ranking(self):
        """Competitors sorted by their rank.

        Update the ranking if needed, that is if `currentturn`
        is higher than `rankedturn`.
        """

        if self.currentturn != self.rankedturn:
            try:
                self.updateRanking()
            except OperationAborted as e:
                # This is most probably caused by the fact that they
                # requested the ranking *after* the new turn has been
                # created: just go on, returning the "old" ranking.
                logger.debug('Match with no result, returning old ranking: %s', e)

        # The rate of the competitor is considered last, so that printing the initial ranking
        # (that is, before first turn), will give the rating ranking
        key = lambda c: (c.prize, c.points, c.bucholz, c.netscore, c.totscore, c.rate)
        return sorted(self.competitors, key=key, reverse=True)

    def updateRanking(self):
        """Recompute competitors ranking.

        Update each competitor rank by examining the matches of this
        tourney, summing up each other's current ranking position as
        the bucholz.
        """

        if self.prized:
            raise OperationAborted(
                _('Cannot update rankings after prize-giving!'))

        # Start from scratch, assigning zero to all competitors. Each
        # tuple contains four values, respectively points, netscore,
        # total score and bucholz.
        ranking = {}
        for comp in self.competitors:
            ranking[comp] = [0, 0, 0, 0]

        LOSER_POINTS = 0
        DRAW_POINTS = 1
        WINNER_POINTS = 2

        # First of all, sum up points and netscore
        for match in self.matches:
            winner, loser, score = match.results()
            if score == 0:
                pw = pl = DRAW_POINTS
            else:
                pw = WINNER_POINTS
                pl = LOSER_POINTS
            rw = ranking[winner]
            rw[0] += pw
            rw[1] += score
            if loser:
                rl = ranking[loser]
                rl[0] += pl
                rl[1] -= score

        # Add phantom
        ranking[None] = [0, 0, 0, 0]

        # Then compute the bucholz, summing up each player's
        # competitors points
        for match in self.matches:
            r1 = ranking[match.competitor1]
            r2 = ranking[match.competitor2]
            r1[2] += match.score1
            r2[2] += match.score2
            r1[3] += r2[0]
            r2[3] += r1[0]

        # Finally, persist the results
        for comp in self.competitors:
            r = ranking[comp]
            comp.points = r[0]
            comp.netscore = r[1]
            comp.totscore = r[2]
            comp.bucholz = r[3]
        self.rankedturn = self.currentturn
        self.modified = func.now()

    def makeNextTurn(self):
        """Setup the next turn.

        If there are no matches, build up the first turn using a
        random coupler. Otherwise, using current ranking, create the
        next turn coupling any given competitor with a not-yet-met
        other one that follows him in the ranking.
        """

        if self.prized:
            raise OperationAborted(
                _('Cannot create other turns after prize-giving!'))

        cturn = self.currentturn
        if cturn and cturn != self.rankedturn:
            self.updateRanking()

        # If the tourney is using a rating, create the first turn
        # with the usual rules instead of random couplings
        if self.idrating is not None or cturn:
            self.currentturn = self._makeNextTurn()
        else:
            self._makeFirstTurn()
            self.currentturn = 1
        self.modified = func.now()

    def _makeFirstTurn(self):
        "Create the first turn of a tourney, coupling competitors in a random way."

        from random import randint
        from . import Match

        comps = self.competitors[:]
        l = len(comps)
        b = 1
        while l > 0:
            c1 = comps.pop(randint(0, l-1))
            if l == 1:
                c2 = None
            else:
                c2 = comps.pop(randint(0, l-2))
            m = Match(turn=1, board=b, competitor1=c1, competitor2=c2,
                      score1=c2 is None and 25 or 0, score2=0)
            self.matches.append(m)
            l -= 2
            b += 1

    def _serialVisitor(self, a, list, skip):
        """Visit the `list` in order.

        This is a generator, used by the combination maker in the simplest case:
        it yields the position in the list, maintaining the order, of the items
        that haven't played against competitor `a`. `skip` is a set containing
        the previous matches (it contains both `(a,b)` and `(b,a)`). Given that
        the list of competitors is sorted by their rank, this effectively tries
        to combine players with the same strength.
        """

        return (i for i in range(len(list))
                if list[i] is not a and (a, list[i]) not in skip)

    def _dazedVisitor(self, a, list, skip):
        """Visit the `list`, giving precedence to the competitors with the same rank.

        Like `_serialVisitor()` this yields the position in the list
        of the competitors that didn't meet `a`. It starts looking at
        the competitors with the same points, and then goes on with
        the others: this is to delay as much as possible the match
        between the strongest competitors.
        """

        # Competitor `a` is always the first in the list: first count
        # how many have the same points, then if possible iterate over
        # the second half of them, then over the first half, and finally
        # over the remaining items.

        same_points = 0
        for i in list:
            # The list may contain the phantom, ie a None
            if i is not None and i.points == a.points:
                same_points += 1
            else:
                break
        if same_points > 3:
            middle = (same_points + 1) // 2
            for i in range(middle, same_points):
                if list[i] is not a and (a, list[i]) not in skip:
                    yield i
            for i in range(0, middle):
                if list[i] is not a and (a, list[i]) not in skip:
                    yield i
            for i in range(same_points, len(list)):
                if list[i] is not a and (a, list[i]) not in skip:
                    yield i
        else:
            for i in range(len(list)):
                if list[i] is not a and (a, list[i]) not in skip:
                    yield i

    def _combine(self, competitors, done, _level=0):
        """Build the next turn, based on current ranking.

        This recursively tries to build the next turn, coupling
        together competitors that did not already played against
        each other.
        """

        if logger.isEnabledFor(logging.DEBUG):
            def debug(msg, *args):
                logger.debug("%sL%02d "+msg, "="*_level, _level, *args)
            def C(c):
                return c.idcompetitor if c else 0
            from pprint import pformat
            debug("Competitors with points: %s", [
                (C(c),c.points if c is not None else 0) for c in competitors])
            if _level == 0:
                done_matches = {}
                for c1, c2 in done:
                    if c1:
                        l = done_matches.setdefault(C(c1), [])
                        if C(c2) not in l:
                            l.append(C(c2))
                            l = done_matches.setdefault(C(c2), [])
                            l.append(C(c1))
                debug("Done matches:\n%s", pformat(done_matches))
        else:
            debug = None

        if len(competitors)<2:
            if debug:
                debug("Backtracking: no more combinations")
            return None

        try:
            visitor = getattr(self, "_%sVisitor" % self.couplings)
        except AttributeError:
            raise AttributeError("No %r method to couple competitors with"
                                 % self.couplings)

        c1 = competitors[0]
        if debug:
            debug('Looking for a competitor for %d within %s', C(c1),
                  [C(competitors[i]) for i in visitor(c1, competitors, done)])
        for n, i in enumerate(visitor(c1, competitors, done)):
            c2 = competitors[i]
            if debug:
                debug("Tentative %d: trying %d,%d", n+1, C(c1), C(c2))
            if len(competitors)>2:
                remainings = self._combine(
                    [c for c in competitors if c is not c1 and c is not c2],
                    done, _level=_level+1)
                if remainings:
                    newturn = [(c1, c2)] + remainings
                    if debug:
                        debug("OK => %s", [(C(_c1), C(_c2))
                                           for _c1, _c2 in newturn])
                    return newturn
            else:
                if debug:
                    debug("OK => %d,%d", C(c1), C(c2))
                return [(c1, c2)]

    def _assignBoards(self, matches, comp_boards, available_boards=None):
        """Assign a table to each match, possibly one not already used."""

        if len(matches)==0:
            return True

        if available_boards is None:
            available_boards = range(1, len(matches)+1)

        match = matches[0]
        rem_matches = matches[1:]

        # Try to assign a table not used by both competitors
        for board in available_boards:
            rem_boards = [b for b in available_boards if b != board]
            if (board not in comp_boards[match.competitor1] and
                board not in comp_boards[match.competitor2] and
                self._assignBoards(rem_matches, comp_boards, rem_boards)):
                match.board = board
                return True

        # No solution, pick the first table
        board = available_boards[0]
        match.board = board
        return self._assignBoards(rem_matches, comp_boards,
                                  available_boards[1:])

    def _makeNextTurn(self):
        """Build the next turn of the game."""

        from . import Match

        ranking = self.ranking

        if self.idrating is not None:
            # Reorder the ranking taking into account the rate of each competitors
            # just after the bucholz
            key = lambda c: (c.points, c.bucholz, c.rate, c.netscore, c.totscore)
            ranking = sorted(ranking, key=key, reverse=True)

        done = set()
        last = 0
        # A dictionary with a set of used boards for each competitor,
        # used later by _assignBoards()
        comp_boards = {}
        for m in self.matches:
            if m.turn > last:
                last = m.turn
            c1 = m.competitor1
            c2 = m.competitor2
            done.add((c1, c2))
            done.add((c2, c1))
            if c1 in comp_boards:
                comp_boards[c1].add(m.board)
            else:
                comp_boards[c1] = set([m.board])
            if c2 in comp_boards:
                comp_boards[c2].add(m.board)
            else:
                comp_boards[c2] = set([m.board])

        newturn = last+1
        activecomps = [c for c in ranking if not c.retired]
        # Append the phantom if the number is odd
        if len(activecomps) % 2:
            activecomps.append(None)

        combination = self._combine(activecomps, done)
        if combination:
            matches = []
            for c1, c2 in combination:
                m = Match(turn=newturn,
                          competitor1=c1, competitor2=c2,
                          score1=c2 is None and 25 or 0, score2=0)
                matches.append(m)
                # Take care of newly registered competitors
                if c1 not in comp_boards:
                    comp_boards[c1] = set()
                if c2 not in comp_boards:
                    comp_boards[c2] = set()

            self._assignBoards(matches, comp_boards)
            self.matches.extend(matches)
        else:
            raise OperationAborted(
                _("Cannot create another turn: No more combinations!"))
        return newturn

    def assignPrizes(self):
        """Consolidate final points."""

        if self.prized:
            raise OperationAborted(
                _('Cannot update prizes after prize-giving!'))

        kind = (self.championship.prizes.capitalize()
                if self.championship.prizes else "Fixed")

        name = "_assign%sPrizes" % kind

        try:
            method = getattr(self, name)
        except AttributeError:
            raise AttributeError("No %r method to assign prizes with" % kind)

        method()

        self.prized = True
        self.modified = func.now()

        if self.rating is not None:
            self.rating.recompute(self.date)

    def _assignAsisPrizes(self):
        "Assign player's points as final prizes."

        for c in self.ranking:
            c.prize = c.points

    def _assignFixedPrizes(self, prizes=None):
        "Assign fixed prizes to the first 16 players."

        if prizes is None:
            # This is what Scarry used to do.
            prizes = [18, 16, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

        for c in self.ranking:
            if prizes:
                prize = prizes.pop(0)
            else:
                prize = 0
            c.prize = prize

    def _assignFixed40Prizes(self):
        "Assign fixed prizes to the first 40 players."

        # This is the Francesco Beltrami's series of prizes, used
        # in the 2009-2010 italian national championship.
        self._assignFixedPrizes(prizes=[
            1000, 900, 800,
            750, 700, 650, 600, 550, 500, 450, 400,
            375, 350, 325, 300, 275, 250, 225, 200, 175, 150,
            140, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40,
            35, 30, 25, 20, 15, 10, 5,
            1])

    def _assignMillesimalPrizes(self):
        "Assign 1000 points to the winner stepping down in fixed amount."

        # This is how the FIC currently assigns the prizes.

        ranking = self.ranking
        prize = 1000
        fraction = prize // len(ranking)
        for c in ranking:
            c.prize = prize
            prize -= fraction

    def _assignWeightedPrizes(self):
        "Similar to 'millesimal' but takes into account previous championship ranking."

        # Compute the "value" of each player by summing his results of
        # the previous championship and dividing by 100 (or 1, if it was a
        # "fixed" prizing championship)
        if self.championship.previous:
            dates, prizes = self.championship.previous.championshipRanking()
            if self.championship.previous.prizes and self.championship.previous.prizes.startswith('fixed'):
                divisor = 1
            else:
                divisor = 100
            pvalues = dict((players, int(sum(details)/divisor))
                           for players, totprize, details, nprizes, skipped in prizes)
        else:
            pvalues = {}

        ranking = self.ranking
        n = len(ranking)

        # Compute the "value" of the whole tourney, summing players values,
        # giving 5 points to those who didn't partecipate to the previous
        # championship
        value = sum(pvalues.get((c.player1, c.player2,
                                 c.player3, c.player4), 5)
                    for c in ranking)

        # Round it to be a multiple of N
        if value % n:
            prize = value + (n - (value % n))
        else:
            prize = value

        fraction = prize // n
        for c in ranking:
            c.prize = prize
            prize -= fraction

    def resetPrizes(self):
        """Reset assigned final points."""

        for c in self.competitors:
            c.prize = 0.0

        self.prized = False
        self.modified = func.now()
        if self.rating is not None:
            self.rating.recompute(self.date)

    def replay(self, date):
        """Clone this tourney, creating new one at given date.

        Of the original, only the competitors are copied.
        This is particularly useful for doubles (or team),
        so that the players get copied in the same order.
        """

        from . import Competitor, Championship

        new = Tourney(date=date,
                      description=_('Replica of $tourney',
                                    mapping=dict(tourney=self.description)),
                      duration=self.duration, prealarm=self.prealarm,
                      location=self.location, couplings=self.couplings,
                      idrating=self.idrating)

        if not self.championship.closed:
            championship = self.championship
        else:
            s = object_session(self)
            championship = s.query(Championship).filter_by(idclub=self.championship.idclub,
                                               closed=False).first()
            if championship is None:
                raise OperationAborted(
                    _('Cannot replicate tourney, no open championships!'))

        championship.tourneys.append(new)

        append = new.competitors.append
        for c in self.competitors:
            append(Competitor(player1=c.player1,
                              player2=c.player2,
                              player3=c.player3,
                              player4=c.player4))
        return new

    def serialize(self, serializer):
        "Reduce a single tourney to a simple dictionary"

        simple = {}
        simple['guid'] = self.guid
        simple['modified'] = self.modified
        simple['championship'] = serializer.addChampionship(self.championship)
        if self.idrating:
            simple['rating'] = serializer.addRating(self.rating)
        simple['description'] = self.description
        simple['date'] = self.date
        if self.location:
            simple['location'] = self.location
        simple['currentturn'] = self.currentturn
        simple['rankedturn'] = self.rankedturn
        simple['prized'] = self.prized
        simple['couplings'] = self.couplings
        simple['duration'] = self.duration
        simple['prealarm'] = self.prealarm

        cmap = {None: None}
        ctors = simple['competitors'] = []

        for i, c in enumerate(self.competitors):
            cmap[c.idcompetitor] = i+1
            sctor = c.serialize(serializer)
            ctors.append(sctor)

        matches = simple['matches'] = []
        for m in self.matches:
            sm = m.serialize(serializer, cmap)
            matches.append(sm)

        return simple
