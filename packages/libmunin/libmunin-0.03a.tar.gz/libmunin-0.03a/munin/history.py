#!/usr/bin/env python
# encoding: utf-8

"""This module implements the history mechanism of libmunin.
"""

# Stdlib:
from itertools import chain
from collections import deque, Counter, OrderedDict, defaultdict
from contextlib import contextmanager
from time import time

# External:
from pymining import itemmining

###########################################################################
#                         Association Rule Mining                         #
###########################################################################


def append_rule(
        data, visited, rules, known_rules, support, left, right,
        min_confidence, min_kulc, max_ir
):
    """Internal Function. Append a rule if it's good enoguh to `rules`.

    :param visited: Set of visited pairs.
    :param known_rules: Rules that are known, and do not need to be recaclulated.
    :param support: Support count for this rule.
    """
    visited.add((left, right))
    if not all((right, left, right in data, left in data)):
        return

    if (left, right) in known_rules or (right, left) in known_rules:
        return

    supp_left = data.get(left)
    confidence = support / supp_left
    if confidence < min_confidence:
        return

    # Kulczynski Measure for consistent rule correlation.
    # [0, 1.0], higher is better.
    # Compare: "Data Mining - Concepts and Techniques" Page 268
    supp_right = data[right]
    kulc = (support / supp_right + support / supp_left) / 2
    if kulc < min_kulc:
        return

    # Imbalance Ratio of the Rule.
    # [0, 1.0], lower is better.
    # Compare: "Data Mining - Concepts and Techniques" Page 270
    ir = abs((supp_left - supp_right) / (supp_left + supp_right - support))
    if ir >= max_ir:
        return

    # Finally add the rule, after all those tests.
    rules.append((left, right, support, (1.0 - ir) * kulc))

    # Lookup set, so we don't calculate the same rule more than once.
    known_rules.add((left, right))


def association_rules(data, min_confidence=0.5, min_support=2, min_kulc=0.66, max_ir=0.35):
    """Compute strong association rules from the itemset_to_support dict in data.

    Inspiration for some tricks in this function were take from:

        https://github.com/bartdag/pymining/blob/master/pymining/assocrules.py

    The rating of a rule is defined as: (1 - imbalance_ratio) * kulczynski

    :param data: Mapping between itemsets and support counts
    :type data: dict(set=int)

    Fine grained finetuning is possible with the following parameters:

    :param min_confidence: Minimal confidence a rule must have (from 0 to 1, higher is better)
    :type min_confidence: float
    :param min_support: Minimal support an itemset must have.
                        Lowers ones are filtered out and only used for lookup.
    :type min_support: int
    :param min_kulc: Minimum Kulczynski measure (from 0 to 1, higher is better)
    :type min_kulc: float
    :param max_ir: Maximum Imbalance Ratio (from 0 to 1, lower is better)
    :type max_ir: float
    :returns: An iterable with rules.
    :rtype: [(left, right, support, rating), ...]
    """
    visited, rules, known_rules = set(), deque(), set()

    # Sort data items by their size, large itemsets first:
    data_items = sorted((
        (itemset, supp) for itemset, supp in data.items()
        if supp >= min_support and len(itemset) > 1
    ), key=lambda tup: len(tup[0]))

    for itemset, support in data_items:
        # Now, build all (senseful) partions of the itemset:
        for item in itemset:
            # Start with one left=item, right=rest
            left, right = frozenset([item]), itemset.difference([item])

            while len(right) is not 0 and (left, right) not in visited:
                # We copy right, so it does not get harmed during iteration:
                for item in chain(right, [None]):
                    append_rule(
                        data, visited, rules, known_rules,
                        support, left, right, min_confidence,
                        min_kulc, max_ir
                    )
                    if item is not None:
                        cap = [item]
                        left, right = left.union(cap), right.difference(cap)

    return rules


###########################################################################
#                         History Implementation                          #
###########################################################################


class History:
    """A History implements a mechanism to store groups of songs together
    that were listened in a certain order.

    Songs can be feeded to the history. Songs that were feeded at the same time
    get into the same group, after some time threshold has passed, a new group
    is opened. A group may only have a certain size, if the size is exceeded
    a new group is opened.

    The whole history can be set to store only a certain amount of groups.
    If new groups are added, the oldest ones are removed.
    """
    def __init__(self, maxlen=100, time_threshold_sec=1200, max_group_size=5):
        """Instance a new History object with these settings:

        :param maxlen: Max. number of groups that may be fed to the history.
        :param time_threshold_sec: Time after which a new group is opened, even
                                   if the current group is not yet full.
        :param max_group_size: Max. size of a single group.
        """
        self._buffer = deque(maxlen=maxlen)
        self._current_group = []
        self._time_threshold_sec, self._max_group_size = time_threshold_sec, max_group_size

    def __iter__(self):
        'Iterate over all songs in the history'
        return chain.from_iterable(self.groups())

    def __reversed__(self):
        'Iterate over all songs in the history in the reverse order, newest first'
        for group in reversed(self.groups()):
            for song in reversed(list(group)):
                yield song
        # return chain.from_iterable(reversed(self.groups()))

    def last_time(self):
        """Gives the last inserted timestamp, or if empty, the current time"""
        # Check if we have a current group:
        if self._current_group:
            return self._current_group[-1][1]

        # Return the current time instead:
        return time()

    def feed(self, song):
        """Feed a single song to the History.

        :param song: The song to add to the listen history.
        :type song: A :class:`munin.song.Song`
        :returns: True if a new group was started.
        """
        # Check if we need to clear the current group:
        exceeds_size = len(self._current_group) >= self._max_group_size
        exceeds_time = abs(time() - self.last_time()) >= self._time_threshold_sec

        if exceeds_size or exceeds_time:
            # Add the buffer to the grouplist,
            self._buffer.append(self._current_group)
            self._current_group = []

        # Append a tuple of song and the current time:
        self._current_group.append((song, time()))
        return exceeds_size or exceeds_time

    def clear(self):
        """Clear the history fully.

        Will be as freshly instantiated afterwards.
        """
        self._buffer.clear()
        self._current_group = []

    def groups(self):
        """Return an iterator to iterate over all groups in the History.

        :returns: an iterator that yields a list of iteralbes with songs in it.
        """
        iterables = deque()
        for group in self._buffer:
            iterables.append((song for song, _ in group))

        if self._current_group:
            iterables.append((song for song, _ in self._current_group))

        return iterables

    def count_keys(self):
        """Count the key distribution of the songs in the history

        Not all songs have all keys set.
        This can be helpful to find often missing data.

        :returns: A collections.Counter object with each attribute and their count.
        """
        counter = Counter()
        for song in self:
            counter.update(song.keys())
        return counter

    def count_listens(self):
        """Count the listens of the songs in the history

        :returns: A collections.Counter object with each song and their count.
        """
        counter = Counter()
        for song in self:
            counter[song] += 1

        return counter

###########################################################################
#                        Concrete Implementations                         #
###########################################################################


class ListenHistory(History):
    """A History that holds all recently listened Songs.
    """
    def __init__(self, maxlen=10000, max_group_size=5, time_threshold_sec=1200):
        'Sane defaults are chosen for ``History.__init__``'
        History.__init__(
            self,
            maxlen=maxlen,
            time_threshold_sec=time_threshold_sec,
            max_group_size=max_group_size
        )

    def frequent_itemsets(self, min_support=2):
        """Mine frequent item sets (FIM) using the RELIM algorithm.

        :param min_support: Minimum count of occurences an itemset must have to be returned.
        :returns: A mapping of itemsets to their supportcount.
        :rtype: dict(set=int)
        """
        relim_input = itemmining.get_relim_input(list(self.groups()))
        return itemmining.relim(relim_input, min_support=min_support)

    def find_rules(self, itemsets=None, min_support=2, **kwargs):
        """Find frequent itemsets and try to find association rules in them.

        :param itemsets: A itemset-mapping, as returned by :func:`frequent_itemsets`.
                         If None, the current history will be mined.

        This function takes the same finetuning parameters as :func`association_rules`.

        :returns: An iterable of rules, each rule being a tuple.
        :rtype: [(left, right, support, confidence, kulc, ir), ...]
        """
        if itemsets is None:
            itemsets = self.frequent_itemsets(min_support=min_support)

        rules = association_rules(itemsets, min_support=min_support, **kwargs)
        return sorted(rules, key=lambda x: x[-1], reverse=True)


class RecommendationHistory(History):
    """Save made recommendations in order to filter *bad* recommendations.

    *bad* shall be defined as follows: If a recommendation with e.g. the same
    artist is repeated, even though, the previous recommendation was from this
    artist it's called *bad*. The same applies for the album or even for the genre.

    In this case we might consider to give a *penalty* to those, so that the same
    artist only might be recommended within the range of, say, 3 recommendations,
    and the same album might only be recommended in the range of 5 recommendations.

    The :class:`RecommendationHistory` can do this for any attribute you might
    think of.
    """
    def __init__(self, penalty_map={'artist': 3, 'album': 5}, **kwargs):
        """
        .. note::

            This takes the same keyword arguments as :class:`History`, but
            ``maxlen`` will be silenty ignored.

        :param penalty_map: A mapping from :term:`attribute` s to a penalty count
                            i.e. the number of recommendations to wait before
                            allowing it again.
        """
        # Hijack the users input, hope he doesn't see this line and gets angry.
        max_group_size = kwargs.setdefault('max_group_size', 5)
        kwargs['maxlen'] = max(penalty_map.values()) // max_group_size + 1
        History.__init__(self, **kwargs)

        self._penalty_map = penalty_map

    def allowed(self, recommendation):
        """Check if a recommendation is allowed, i.e. if it someting similar
        was not recently recommended.

        :param recommendation: The recommendation to check for forbidden attributes.
        :type recommendation: :class:`munin.song.Song`
        :returns: True if it is allowed, i.e. all possibly forbidden attributes
                  are long enough ago.
        """
        for attribute, penalty in self._penalty_map.items():
            forbidden = recommendation.get(attribute)
            if forbidden is None:
                continue

            for idx, song in enumerate(reversed(self)):
                if idx >= penalty:
                    break

                comparable = song.get(attribute)
                if comparable is None:
                    continue

                if comparable == forbidden:
                    return False

        return True


###########################################################################
#                             Rule Management                             #
###########################################################################

def _sort_by_rating(elem):
    return elem[-1]


class RuleIndex:
    """A Manager for all known and usable rules.

    This class offers an Index for all rules, so one can ask
    for all rules that affect a certain song. Additionally
    the number of total rules are limited by specifying a maxlen.
    If more rules are added they become invalid and get deleted on the
    next add or once all adds were done (with :func:`begin_add_many`).

    Duplicated rules are silently ignored.

    This class implements the contains operator to check if a rule tuple
    is in the index. Also ``__iter__`` is supported, and will yield
    the rules in the index sorted by their Kulczynski measure multiplied
    by their imbalance ratio.
    """

    def __init__(self, maxlen=1000):
        """Create a new Index with a certain maximal length:

        :param maxlen: Max. number of rules to save, or 0 for no limit.
        """
        self._max_rules = maxlen or 2 ** 100
        self._rule_list = OrderedDict()
        self._rule_dict = defaultdict(set)
        self._rule_cuid = 0

    def __iter__(self):
        """Iterate over all rules in a sorted way.

        Requires O(n log n). This could be optimized.
        """
        return iter(sorted(self._rule_list.values(), key=lambda rule: 1.0 - rule[-1]))

    def __contains__(self, rule_tuple):
        'Check if a rule tuple is in the index. Only considers songs in it.'
        return bool(self.locate(rule_tuple))

    def _locate(self, rule_tuple):
        """Locate the the first rule_tuple and rule_uid with same left/right.

        :returns: a tuple of (rule_uid, rule_tuple)
        """
        first_song = next(iter(rule_tuple[0]))
        lefts, rights, *_ = rule_tuple
        candidate_ids = set()

        # Locate all rules that contain a song in the input rule
        for uid in self._rule_dict.get(first_song, ()):
            if uid in self._rule_list:
                candidate_ids.add(uid)

        # Check those for left/right idendity (instead of checking all rules)
        for uid in candidate_ids:
            stored_tuple = self._rule_list[uid]
            stored_lefts, stored_rights, *_ = stored_tuple

            if lefts == stored_lefts and rights == stored_rights:
                return uid, stored_tuple

            if rights == stored_lefts and lefts == stored_rights:
                return uid, stored_tuple

        return None, None

    def best(self):
        """Return the currently best rule (the one with the highest rating)

        Requires linear complexity. This could be optimized.

        :returns: A ruletuple or None if no rule yet in the index.
        """
        try:
            return max(self._rule_list.values(), key=lambda rule: rule[-1])
        except ValueError:
            return None

    def insert_rules(self, rule_tuples):
        """Convienience function for adding many rules at once.

        Calls :func:`drop_invalid` when done inserting.

        :param rule_tuples: a list of rule tuples.
        """
        with self.begin_add_many():
            for rule in rule_tuples:
                self.insert_rule(rule, drop_invalid=False)

    def insert_rule(self, rule_tuple, drop_invalid=False):
        """Add a new rule to the index.

        :param rule_tuple: The rule to add, coming from :func:`association_rules`.
        :param drop_invalid: If True, delete the first element
                             immediately if index is too large.
        """
        # Step 0: Check if we already know that item.
        stored_uid, stored_rule = self._locate(rule_tuple)

        # Update if the rating is better:
        if stored_rule is not None and rule_tuple[-1] > stored_rule[-1]:
            self._rule_list[stored_uid] = rule_tuple
            return

        # Step 1: Add the affected songs to the index:
        left, right, *_ = rule_tuple
        for song in chain(left, right):
            self._rule_dict[song].add(self._rule_cuid)

        # Step 2: Remember this rule, so we can look it up later.
        self._rule_list[self._rule_cuid] = rule_tuple
        self._rule_cuid += 1

        # Step 3: Prune the index, if too big.
        if len(self._rule_list) > self._max_rules:
            fst_uid, fst_rule = self._rule_list.popitem(last=False)
            if drop_invalid:
                for uid_set in self._rule_dict.values():
                    uid_set.discard(fst_uid)

    def lookup(self, song):
        """Lookup all rules that would affect a certain song.

        :param song: The song to lookup.
        :type song: :class:`munin.song.Song`
        :returns: An iterable with all rule_tuples affecting this song.
        """
        for uid in self._rule_dict.get(song, ()):
            if uid in self._rule_list:
                yield self._rule_list[uid]

    @contextmanager
    def begin_add_many(self):
        """Contextmanager for adding many songs.

        ::

            >>> with rule_index.begin_add_many():
            ...    rule_index.insert_rule(...)

        Calls :func:`drop_invalid` after being done.
        """
        try:
            yield
        finally:
            self.drop_invalid()

    def drop_invalid(self):
        """Delete invalid rules from the cache.

        Often, a large number of rules is added at once.
        For maintaining a valid index, rules that are no longer valid
        need to be deleted from the cache, which takes linear time.

        With this, the cache is checked for consistenct only once all rules
        were added, which might be a lot faster for many rules.
        """
        # Prune invalid items (if any)
        for uid_set in self._rule_dict.values():
            for uid in list(uid_set):
                if not uid in self._rule_list:
                    uid_set.remove(uid)

###########################################################################
#                               Unit Tests                                #
###########################################################################

if __name__ == '__main__':
    import unittest

    from random import choice, shuffle
    from munin.song import Song
    from munin.session import Session

    class RuleIndexTest(unittest.TestCase):
        def setUp(self):
            self._idx = RuleIndex(maxlen=10)

        def test_insert_normal(self):
            N = 20

            for setting in [False, True] * 10:
                self._idx = RuleIndex(maxlen=10)
                songs = ['one', 'two', 'three', 'four']

                # Feed random input to the history:
                for i in range(N, 0, -1):
                    shuffle(songs)
                    self._idx.insert_rule(
                            (
                                frozenset(songs[:2]),
                                frozenset(songs[2:]),
                                0.1, 1 - i / N, i / N * 0.5
                            ),
                            drop_invalid=setting
                    )

                # Check if we still cann access it:
                for left, right, *_ in self._idx.lookup('one'):
                    self.assertTrue('one' in left or 'one' in right)

                # Check the number of items in the index:
                self.assertEqual(len(self._idx._rule_list), 10)
                self.assertEqual(len(self._idx._rule_dict), 4)
                for value in self._idx._rule_dict.values():
                    if setting is False:
                        self.assertEqual(len(value), N)
                    else:
                        self.assertEqual(len(value), 10)

                # Invalidate the cache for this setting:
                if setting is False:
                    self._idx.drop_invalid()
                    for value in self._idx._rule_dict.values():
                        self.assertEqual(len(value), 10)

                # Check if iteration works:
                iterated = [rating for *_, rating in self._idx]
                resorted = sorted(iterated, reverse=True)

                for l, r in zip(iterated, resorted):
                    self.assertAlmostEqual(l - r, 0.0)

    class HistoryTest(unittest.TestCase):
        def setUp(self):
            self._session = Session('test', {
                'a': (None, None, 1.0),
                'b': (None, None, 1.0),
                'c': (None, None, 1.0),
                'd': (None, None, 1.0),
                'e': (None, None, 1.0),
                'f': (None, None, 1.0)
            })

        def test_count_keys(self):
            history = History(maxlen=19)
            for _ in range(2000):
                history.feed(Song(self._session, {choice('abcdef'): 1.0}))

            counter = history.count_keys()
            for char in 'abdef':
                self.assertTrue(char in counter)

            self.assertEqual(sum(counter.values()), 100)
            self.assertEqual(len(list(history.groups())), 20)
            for group in history.groups():
                self.assertEqual(len(list(group)), 5)

        def test_recommendation_history(self):
            history = RecommendationHistory()
            session = Session('test',
                {'artist': (None, None, 1), 'album': (None, None, 1)}
            )
            fst_song = Song(session, {
                'artist': 'A',
                'album': 'B'
            })

            self.assertEqual(history.allowed(fst_song), True)
            history.feed(fst_song)
            self.assertEqual(history.allowed(fst_song), False)

            for expectation in [False, False, False, False, True]:
                history.feed(Song(session, {
                    'artist': 'X',
                    'album': 'Y'
                }))
                self.assertEqual(history.allowed(fst_song), expectation)

        def test_relim(self):
            history = ListenHistory()

            songs = [Song(self._session, {'abcdef'[idx]: 1.0}) for idx in range(6)]
            for idx, song in enumerate(songs):
                song.uid = idx

            N = 10000
            for _ in range(N):
                for i, ilem in enumerate(songs):
                    history.feed(ilem)
                    for j, jlem in enumerate(songs[i:]):
                        history.feed(jlem)

            itemsets = history.frequent_itemsets()

            print()
            print('==================')
            print('FREQUENT ITEMSETS:')
            print('==================')
            print()
            for itemset, support in sorted(itemsets.items(), key=lambda x: x[1]):
                print('{: 8d} ({:3.3f}%): {:>20s}'.format(
                    support, support / N * 10,
                    str([song.uid for song in itemset])
                ))

            print()
            print('==================')
            print('ASSOCIATION RULES:')
            print('==================')
            print()

            rules = history.find_rules(itemsets)
            for left, right, support, rating in rules:
                print('{:>15s} <-> {:<15s} [supp={:> 5d}, rating={:.5f}]'.format(
                    str([song.uid for song in left]),
                    str([song.uid for song in right]),
                    support, rating
                ))

    unittest.main()
