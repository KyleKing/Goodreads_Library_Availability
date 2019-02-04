import json
from os import getcwd
from os.path import isfile, join

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
    ('City of Pearl', 'Karen Traviss'),
    ('electronic resource', 'NA')
])
def test_getSoup(title, author):
    if not isfile(getSnippetFn(formatQuery(title))):
        getSoup(title)


def prepParseSoup(title):
    print('\n>> Parsing Title: {}'.format(title))
    fn = getSnippetFn(formatQuery(title))
    print('Opening: {}'.format(join(getcwd(), fn)))
    with open(fn, 'r') as snippetFile:
        soup = BeautifulSoup(snippetFile, 'html.parser')
    books = parseSoup(soup)
    print(json.dumps(books, indent=4, separators=(',', ': ')))
    return books


def test_parseSoup_oneMatch():
    """Test when match redirects to view a single book."""
    title, author = ('Shade: A Tale of Two Presidents', 'Pete Souza')
    books = prepParseSoup(title)
    assert len(books) == 1
    book = books[0]
    assert book['title'] == 'Shade : a tale of two presidents'  # slight difference in library title
    assert book['author'] == author
    assert book['format'] == '235 pages : color illustrations ; 24 cm'


def test_parseSoup_noAccurateMatch():
    # Match books with similar titles, but all different authors
    title, author = ('Runs in the Family', 'Kevin Ikenberry')
    books = prepParseSoup(title)
    assert len(books) >= 4
    for key in ['title', 'author', 'format']:
        assert all([type(book[key]) is str for book in books])


def test_parseSoup_multipleGoodMatches():
    title, author = ('Old Man\'s War', 'John Scalzi')  # 2nd result is correct
    books = prepParseSoup(title)
    # Check that 1 page (12 matches) and the first two have the same author
    assert len(books) == 12
    for book in books[:2]:
        assert book['title'].split(' ')[0] == title.split(' ')[0]
        assert book['author'] == author


def test_parseSoup_electronicResource():
    books = prepParseSoup('electronic resource')
    assert len(books) == 12
    assert all([book['eResource'] is True for book in books])
    for key in ['kindle', 'physical', 'audio']:
        assert all([book[key] is False for book in books])
