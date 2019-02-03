"""Use bs4 to search the Moco library."""

import json
import os
import re
import time
from difflib import get_close_matches
from os import path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

import jsonlines
from selenium import webdriver

base = 'https://mdpl.ent.sirsi.net/client/en_US/catalog/search/results'
mocoURL = '{}?qu={}&{}'.format(base, '{query}', '&te=&rt=false%7C%7C%7CTITLE%7C%7C%7CTitle')

jsonlFn = 'rawMatches.jsonl'
open(jsonlFn, 'w').close()


def saveSnippet(query, soup):

    if not path.isdir('raw'):
        os.makedirs('raw')
    # Try to identify the minimum HTML to grab
    content = soup.find('div', 'detail_main_wrapper')
    if content is None:
        content = soup.find('div', {'id': 'content'})
    if content is None:
        content = soup

    with open(path.join('raw', query + '.html'), 'w') as htmlFile:
        htmlFile.write(content.prettify())


def filterBooks(filterKwargs, books):
    """Filter matches books dictionary. Return up to 3 best matches.

    filterKwargs -- dictionary to compare against the books argument
    books -- list of books with matching keys to the filter args

    """
    matches = []
    for book in books:
        if type(book['author']) is str:
            if any([_a in book['author'] for _a in filterKwargs['author'].split()]):
                matches.append(book)
        else:
            matches.append(book)
    return matches

    # idxs = []
    # for key in filterKwargs.keys():
    #     items = [book[key] for book in books if type(book[key]) is str]
    #     matches = get_close_matches(filterKwargs[key], items)
    #     idxs += [items.index(match) for match in matches]
    # bestMatches = [books[idx] for n, idx in enumerate(idxs) if idx in idxs[:n]]
    # if len(bestMatches) > 0:
    #     return bestMatches
    # else:
    #     return [books[idx] for idx in list(set(idxs))]


def selectOne(soup_, class_):
    """soup.select() wrapper."""
    # Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class
    selection = soup_.select(class_)
    try:
        items = [sel.string.strip() for sel in selection]
        if len(items) > 1:
            print('With `{}`, found: {}'.format(class_, items))
        # return items[0]
        return '--'.join(items)
    except IndexError:
        return None


def searchLib(title, author='', rawURL=mocoURL):
    """Search the public library for books matching the title and author.

    title -- book title
    author -- (optional) book author
    rawURL -- (optional) URL string that contains '...{query}...'

    """
    query = quote('___'.join(title.split(' '))).replace('___', '+')
    url = rawURL.format(query=query)
    print('\nSearching with query: {}\nURL:{}'.format(query, url))

    # # FYI: enable pagination
    # page = 0
    # startIdx = page * 12
    # url += '&rw={}'.format(url, startIdx)

    # # Alternative with selenium
    # driver = webdriver.Chrome()
    # driver.get(url)
    # time.sleep(10)
    # resp = driver.page_source

    resp = requests.get(url).text
    time.sleep(1)

    soup = BeautifulSoup(resp, 'html.parser')

    saveSnippet(query, soup)
    with open('rawMoco.html', 'w') as outFile:
        outFile.write(soup.prettify())

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
        if type(_author) is str:
            _author = ' '.join(_author.split(',')[::-1])
            _author = re.sub(r'[:\-\.,\d]+', '', _author).replace('author', '').strip()
        else:
            _author = None
        try:
            _title = content.a['title']
        except TypeError:
            _title = selectOne(content, 'a.title')
        if type(_title) is not str:
            _title = selectOne(content, 'div.displayElementText.TITLE')
        if type(_title) is str:
            _title = re.sub(r'[:\.\[\]]', '', _title).replace('electronic resource', '').strip()
            # Remove trailing forward slash and author name
            _title = _title.split('a novel /')[0].strip()
        else:
            _title = None
        _format = selectOne(content, 'div.displayElementText.ERC_FORMAT')
        print('_format: {}'.format(_format))
        books.append({
            'title': _title,
            'author': _author,
            'format': _format
        })

    with open('rawBooks.json', 'w') as jsonFile:
        json.dump(books, jsonFile, indent='\t', separators=(',', ': '))

    # Return the best matches from all books returned in search
    matches = filterBooks({'title': title, 'author': author}, books)
    with jsonlines.open(jsonlFn, 'a') as writer:
        writer.write({'Raw': books, 'matches': matches})
    return matches


def debug(title, author):
    resp = searchLib(title, author)
    # print('title: {}'.format(title))
    # print('author: {}'.format(author))
    print(json.dumps(resp, indent=4, separators=(',', ': ')))
    print('=' * 80)


if __name__ == '__main__':
    debug('Old Man\'s War', 'John Scalzi')  # 2nd result is correct
    debug('The Path of Daggers', 'Robert Jordan')  # Redirects to available paper copies
    debug('Runs in the Family', 'Kevin Ikenberry')  # (No results)
    debug('1Q84', 'Haruki Murakami')  # (Difficult match)
    debug('Lexicon', 'Max Barry')  # (2 results, 1st is correct)
    debug('Shade: A Tale of Two Presidents', 'Pete Souza')  # (goes direct to book...)
    debug('Under the Dome', 'Stephen King')
    debug('Afterlife', 'Marcus Sakey')
    debug('City of Pearl', 'Karen Traviss')
