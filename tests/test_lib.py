import pytest

from gr_lib_sync.lib import parseAuthor, parseTitle


@pytest.mark.parametrize('raw,expected', [
    ('last, first', 'first last'),
    ('author: last, first', 'first last'),
    (' King,  Kyle  \n  ', 'Kyle King'),
    ('Souza, Pete, author.', 'Pete Souza'),
    ('Murakami, Haruki, 1949-', 'Haruki Murakami')
])
def test_parseAuthor(raw, expected):
    assert parseAuthor(raw) == expected


@pytest.mark.parametrize('raw,expected', [
    ('TITLE electronic resource', 'TITLE'),
    ('Old man\'s war / John Scalzi.', 'Old man\'s war'),
    ('1Q84. Part 1 of 2 [sound recording] : a novel / Haruki Murakami.', '1Q84. Part 1 of 2 [sound recording]'),
    ('The path of daggers / Robert Jordan.', 'The path of daggers'),
    ('Reclaiming the Everglades [web site] : South Florida\'s natural history 1884-1934 / American Memory, Library of Congress.', 'Reclaiming the Everglades [web site] : South Florida\'s natural history 1884-1934')  # noqa: E501
])
def test_parseTitle(raw, expected):
    assert parseTitle(raw) == expected
