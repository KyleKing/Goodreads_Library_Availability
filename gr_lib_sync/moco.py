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
    """Return the HTML response for a search of the public library.

    title -- book title
    rawURL -- (optional) URL string that contains '...{query}...'

    """
    query = formatQuery(title)
    url = rawURL.format(query=query)
    print('\nSearching with query: {}\nURL:{}'.format(query, url))

    # # FYI: enable pagination
    # page = 0
    # startIdx = page * 12
    # url += '&rw={}'.format(url, startIdx)

    # # Alternative with selenium
    # from selenium import webdriver
    # driver = webdriver.Chrome()
    # driver.get(url)
    # time.sleep(10)
    # resp = driver.page_source

    snippetFn = getSnippetFn(formatQuery(title))
    if not isfile(snippetFn):
        resp = requests.get(url).text
        time.sleep(1)  # Be kind and rate limit requests

        soup = BeautifulSoup(resp, 'html.parser')
        saveSnippet(query, soup)
        with open('rawMoco.html', 'w') as outFile:
            outFile.write(soup.prettify())
    else:
        with open(snippetFn, 'r') as snippetFile:
            soup = BeautifulSoup(snippetFile, 'html.parser')

    return soup


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
        _author = selectOne(content, 'div.displayElementText.INITIAL_AUTHOR_SRCH')
        if type(_author) is not str:
            _author = selectOne(content, 'div.displayElementText.AUTHOR')
        _author = parseAuthor(_author)
        try:
            _title = content.a['title']
        except TypeError:
            _title = selectOne(content, 'a.title')
        if type(_title) is not str:
            _title = selectOne(content, 'div.displayElementText.TITLE')
        _title = parseTitle(_title)
        _format = selectOne(content, 'div.displayElementText.ERC_FORMAT')
        print('_format: {}'.format(_format))
        books.append({
            'title': _title,
            'author': _author,
            'format': _format
        })
    return books


def searchLib(title, author='', rawURL=mocoURL):
    """Search the public library for books matching the title and author.

    title -- book title
    author -- (optional) book author
    rawURL -- (optional) URL string that contains '...{query}...'

    """
    soup = getSoup(title)
    books = parseSoup(soup)

    with open('rawMoco.json', 'w') as jsonFile:
        json.dump(books, jsonFile, indent='\t', separators=(',', ': '))

    # Return the best matches from all books returned in search
    matches = filterBooks({'title': title, 'author': author}, books)
    writeJLine({'Raw': books, 'matches': matches})
    return matches


def debug(title, author):
    """WIP: Wrapper for searchLib with STDOUT."""
    resp = searchLib(title, author)
    # print('title: {}'.format(title))
    # print('author: {}'.format(author))
    print(json.dumps(resp, indent=4, separators=(',', ': ')))
    print('=' * 80)
