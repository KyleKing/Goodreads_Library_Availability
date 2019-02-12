"""Use bs4 to search the Moco library."""

import json
import time
from os.path import isfile

import requests
from bs4 import BeautifulSoup

from .lib import filterBooks, parseAuthor, parseTitle, saveSnippet, selectOne, writeJLine, formatQuery, getSnippetFn

base = 'https://mdpl.ent.sirsi.net/client/en_US/catalog/search/results'
mocoURL = '{}?qu={}&{}'.format(base, '{query}', '&te=&rt=false%7C%7C%7CTITLE%7C%7C%7CTitle')


def getSoup(title, rawURL=mocoURL):
    """Return tuple of the HTML response for a search of the public library and raw URL.

    title -- book title
    rawURL -- (optional) URL string that contains '...{query}...'

    """
    query = formatQuery(title)
    url = rawURL.format(query=query)

    # # FYI: for pagination...
    # page = 0
    # startIdx = page * 12  # default is 12 books/page
    # url += '&rw={}'.format(url, startIdx)

    snippetFn = getSnippetFn(formatQuery(title))
    if not isfile(snippetFn):
        print('\n>>Searching with query: {}\nURL:{}'.format(query, url))
        resp = requests.get(url).text
        time.sleep(1)  # Be kind and rate limit requests

        soup = BeautifulSoup(resp, 'html.parser')
        saveSnippet(query, soup)
        with open('rawMoco.html', 'w') as outFile:
            outFile.write(soup.prettify())
    else:
        print('\n>>Loading from file for query: {}\nfile:{}'.format(query, snippetFn))
        with open(snippetFn, 'r') as snippetFile:
            soup = BeautifulSoup(snippetFile, 'html.parser')

    return (soup, url)


def parseSoup(soup):
    """Parse HTML for book list.

    soup_ -- HTML from beautiful soup

    """
    searchResult = soup.find('div', {'id': 'searchResultText'})
    if searchResult and 'returned no results' in searchResult.string:
        bookList = []
    else:
        # Soup the results of the search
        bookList = soup.findAll('div', 'results_bio')
        if len(bookList) == 0:
            # Or if only one match was found, soup that div
            bookList = [soup.find('div', {'id': 'detail_biblio0'})]
    # Loop each search results to filter for best matches
    books = []
    for rIdx, content in enumerate(bookList):
        _title = selectOne(content, 'div.displayElementText.INITIAL_TITLE_SRCH')
        if type(_title) is not str:
            _title = selectOne(content, 'div.displayElementText.TITLE')
        if type(_title) is not str:
            _title = selectOne(content, 'a.hideIE')

        _author = selectOne(content, 'div.displayElementText.INITIAL_AUTHOR_SRCH')
        if type(_author) is not str:
            _author = selectOne(content, 'div.displayElementText.AUTHOR')

        book = {
            'title': parseTitle(_title), 'author': parseAuthor(_author),
            'kindle': False, 'eResource': False, 'physical': False, 'audio': False
        }

        _format = selectOne(content, 'div.displayElementText.ERC_FORMAT')
        if type(_format) is not str:
            # Check for physical book
            _format = selectOne(content, 'div.displayElementText.PHYSICAL_DESC')
            if type(_format) is not str:
                isbn = selectOne(content, 'div.displayElementText.ISBN')
                if type(isbn) is str:
                    _format = 'ISBN: {}'.format(isbn)
            if type(_format) is str:
                book['physical'] = True
        else:
            if 'KINDLE' in _format:
                book['kindle'] = True
            elif 'CLOUDLIBRARY' in _format:
                book['eResource'] = True
            elif 'AUDIO' in _format:
                book['audio'] = True

        book['format'] = _format
        books.append(book)
        print('>> book: {}'.format(book))
    return books


def searchLib(title, author='', rawURL=mocoURL):
    """Search the public library for books matching the title and author. Return tuple of matches and raw URL.

    title -- book title
    author -- (optional) book author
    rawURL -- (optional) URL string that contains '...{query}...'

    """
    soup, url = getSoup(title)
    books = parseSoup(soup)

    with open('rawMoco.json', 'w') as jsonFile:
        json.dump(books, jsonFile, indent='\t', separators=(',', ': '))

    # Return the best matches from all books returned in search
    matches = filterBooks({'title': title, 'author': author}, books)
    writeJLine({'Raw': books, 'matches': matches})
    return (matches, url)


def debug(title, author):
    """WIP: Wrapper for searchLib with STDOUT."""
    resp, url = searchLib(title, author)
    # print('title: {}'.format(title))
    # print('author: {}'.format(author))
    print(json.dumps(resp, indent=4, separators=(',', ': ')))
    print('=' * 80)
