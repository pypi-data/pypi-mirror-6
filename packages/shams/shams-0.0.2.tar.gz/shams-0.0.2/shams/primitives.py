from __future__ import unicode_literals

import string
from random import choice, randint
from urllib import urlencode
from urlparse import urlunsplit

CHARS = (
    string.lowercase.decode('utf-8') +
    ''.join(set(''.join(unichr(i) for i in range(192, 300)).lower()))
)


def word(min=2, max=10, charset=None):
    charset = charset or CHARS
    return ''.join(choice(charset) for i in range(randint(min, max)))


def _words(word_func, num=3, **kwargs):
    return ' '.join(word_func(**kwargs) for i in range(num))


def lowercase_word(*args, **kwargs):
    return word(**kwargs).lower()


def uppercase_word(*args, **kwargs):
    return word(**kwargs).upper()


def capital_word(*args, **kwargs):
    return word(**kwargs).capitalize()


def words(*args, **kwargs):
    return _words(word, **kwargs)


def random_words(min, max, *args, **kwargs):
    num = randint(min, max)
    return words(num=num, *args, **kwargs)


def lowercase_words(*args, **kwargs):
    return _words(lowercase_word, **kwargs)


def random_lowercase_words(min, max, *args, **kwargs):
    num = randint(min, max)
    return lowercase_words(num=num, *args, **kwargs)


def uppercase_words(*args, **kwargs):
    return _words(uppercase_word, **kwargs)


def random_uppercase_words(min, max, *args, **kwargs):
    num = randint(min, max)
    return uppercase_words(num=num, *args, **kwargs)


def capital_words(*args, **kwargs):
    return _words(capital_word, **kwargs)


def random_capital_words(min, max, *args, **kwargs):
    num = randint(min, max)
    return capital_words(num=num, *args, **kwargs)


def number(min, max):
    return randint(min, max)


def url():
    scheme = choice(('http', 'https'))
    tld = choice(('com', 'org', 'net', 'edu', 'gov'))
    charset = (
        string.digits +
        string.lowercase +
        string.uppercase
    ).decode('utf-8')
    netloc = '.'.join((
        random_words(1, 4, charset=charset).replace(' ', '.'),
        tld,
    ))
    path = random_words(1, 4, charset=charset).replace(' ', '/')
    query = urlencode(dict(words(
        num=2, charset=charset).split(' ') for i in range(randint(1, 4))))
    fragment = word(charset=charset)
    return urlunsplit((scheme, netloc, path, query, fragment))
