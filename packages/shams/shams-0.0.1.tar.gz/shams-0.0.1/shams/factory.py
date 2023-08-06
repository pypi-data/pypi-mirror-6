from __future__ import unicode_literals, absolute_import

from random import choice

from factory import Sequence
from localflavor.us.us_states import US_STATES

from . import primitives


class Sham(Sequence):

    def __init__(self):
        super(Sham, self).__init__(self.value)

    def value(self, n):
        raise NotImplementedError('Subclasses must implement this.')


class Name(Sham):

    def __init__(self, min_words=2, max_words=2):
        self.min_words = min_words
        self.max_words = max_words
        super(Name, self).__init__()

    def value(self, n):
        return primitives.random_capital_words(self.min_words, self.max_words)


class Blob(Sham):

    def __init__(self, min_words=100, max_words=100):
        self.min_words = min_words
        self.max_words = max_words
        super(Blob, self).__init__()

    def value(self, n):
        return primitives.random_words(self.min_words, self.max_words)


class Number(Sham):

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max
        super(Number, self).__init__()

    def value(self, n):
        if self.min and self.max:
            return primitives.number(self.min, self.max)
        return n


class UnicodeNumber(Number):

    def __init__(self, digits=None, *args, **kwargs):
        self.digits = digits
        super(UnicodeNumber, self).__init__(*args, **kwargs)

    def value(self, n):
        val = unicode(super(UnicodeNumber, self).value(n))
        if self.digits:
            val = val.zfill(self.digits)[:self.digits]
        return val

# TODO: support other phone formats


class Phone(Sham):

    def value(self, n):
        return '-'.join(
            unicode(primitives.number(0, 10 ** i - 1)) for i in (3, 3, 4))


class Url(Sham):

    def value(self, n):
        return primitives.url()


class StreetAddress(Sham):

    def value(self, n):
        suffixes = ('St', 'Ave', 'Ln', 'Blvd', 'Rd')
        return '{0} {1} {2}.'.format(
            primitives.number(1, 10 ** 5),
            primitives.random_capital_words(1, 3),
            choice(suffixes),
        )


class State(Sham):

    def __init__(self, short_name=False):
        self.short_name = short_name
        super(State, self).__init__()

    def value(self, n):
        index = 0 if self.short_name else 1
        return choice([s[index] for s in US_STATES]).decode('utf-8')


class ZipCode(UnicodeNumber):

    def __init__(self):
        super(ZipCode, self).__init__(digits=5, min=1, max=10 ** 5 - 1)
