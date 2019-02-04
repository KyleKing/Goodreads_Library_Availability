import json
from os.path import isfile

import pytest
from bs4 import BeautifulSoup

from gr_lib_sync.lib import formatQuery, getSnippetFn
from gr_lib_sync.moco import getSoup, parseSoup


@pytest.mark.parametrize('title,author', [
    ('Old Man\'s War', 'John Scalzi'),  # 2nd result is correct
    ('The Path of Daggers', 'Robert Jordan'),  # Redirects kindle search to general search
    ('Runs in the Family', 'Kevin Ikenberry'),  # (No results)
    ('1Q84', 'Haruki Murakami'),  # (Difficult match)
    ('Lexicon', 'Max Barry'),  # (2 results, 1st is correct)
    ('Shade: A Tale of Two Presidents', 'Pete Souza'),
    ('Under the Dome', 'Stephen King'),
    ('Afterlife', 'Marcus Sakey'),
    ('City of Pearl', 'Karen Traviss')
])
def test_getSoup(title, author):
    if not isfile(getSnippetFn(formatQuery(title))):
        getSoup(title)


def prepParseSoup(title):
    print('\n>> Parsing Title: {}'.format(title))
    with open(getSnippetFn(formatQuery(title)), 'r') as snippetFile:
        soup = BeautifulSoup(snippetFile, 'html.parser')
    books = parseSoup(soup)
    print(json.dumps(books, indent=4, separators=(',', ': ')))
    return books


def test_parseSoup_oneMatch():
    """Test when match redirects to view a single book."""
    title, author = ('Shade: A Tale of Two Presidents', 'Pete Souza')
    books = prepParseSoup(title)


def test_parseSoup_noGoodMatch():
    title, author = ('Shade: A Tale of Two Presidents', 'Pete Souza')
    books = prepParseSoup('Runs in the Family')


def test_parseSoup_multipleGoodMatches():
    title, author = ('Old Man\'s War', 'John Scalzi')  # 2nd result is correct
    books = prepParseSoup(title)


if __name__ == '__main__':
    test_parseSoup_oneMatch()
