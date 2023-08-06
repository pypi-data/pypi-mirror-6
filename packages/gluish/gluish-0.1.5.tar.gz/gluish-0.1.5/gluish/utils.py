# coding: utf-8

"""
Various utilities.
"""

from dateutil import relativedelta
from gluish.shell import shellout
import collections
import itertools
import random
import re
import string


class DotDict(dict):
    __getattr__= dict.__getitem__

    def __init__(self, d):
        self.update(**dict((k, self.parse(v))
                           for k, v in d.iteritems()))

    @classmethod
    def parse(cls, value):
        """ Parse the dict value. """
        if isinstance(value, dict):
            return cls(value)
        elif isinstance(value, list):
            return [cls.parse(i) for i in value]
        else:
            return value


def flatten(iterable):
    """
    Flattens arbitrary nested lists into a flat list. """
    for item in iterable:
        if (isinstance(item, collections.Iterable) and
            not isinstance(item, basestring)):
            for sub in flatten(item):
                yield sub
        else:
            yield item


def pairwise(obj):
    """ Iterator over a iterable in steps of two. """
    iterable = iter(obj)
    return itertools.izip(iterable, iterable)


def nwise(iterable, n=2):
    """
    Generalized :func:`pairwise`.
    Split an iterable after every `n` items.
    """
    i = iter(iterable)
    piece = tuple(itertools.islice(i, n))
    while piece:
        yield piece
        piece = tuple(itertools.islice(i, n))


def download(url=None, filename=None):
    """ Download a URL content to filename. """
    shellout("""wget -q --retry-connrefused -O {output} '{url}' """,
             url=url, output=filename)


def date_range(start_date, end_date, increment, period):
    """
    Generate `date` objects between `start_date` and `end_date` in `increment`
    `period` intervals.
    """
    result = []
    nxt = start_date
    delta = relativedelta.relativedelta(**{period:increment})
    while nxt <= end_date:
        result.append(nxt)
        nxt += delta
    return result


def normalize(s):
    """
    Quick and dirty string normalizer.
    """
    return ' '.join(re.sub('[^a-zA-Z0-9 ]', '', s).lower().split())


def random_string(length=16):
    """
    Return a random string (upper and lowercase letters) of length `length`,
    defaults to 16.
    """
    return ''.join(random.choice(string.letters) for _ in range(length))


def dashify(s):
    """
    Convert CamelCase to camel-case,
    http://stackoverflow.com/a/1176023/89391.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', s)
    result = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
    return istrip(result)


def istrip(s):
    """
    Remove all spaces and newlines from a string.
    """
    return re.sub(r'\s+', '', s.strip().replace('\n', ''))


def unwrap(s):
    """
    Remove newlines and repeated spaces from a string.
    """
    if not isinstance(s, basestring):
        return s
    s = re.sub(r'\s+', ' ', s.strip().replace('\n', ''))
    return s
