"""General Library HTML-Parsing functions"""

import os
import re
from os.path import isdir, join
from urllib.parse import quote

import jsonlines

jsonlFn = 'rawMatches.jsonl'
open(jsonlFn, 'w').close()


def writeJLine(obj):
    """Append to the JSON Lines output file.

    obj -- JSON object

    """
    with jsonlines.open(jsonlFn, 'a') as writer:
        writer.write(obj)


def formatQuery(title):
    """Safely format the title into a valid query slug.

    title -- book title

    """
    return quote('___'.join(title.split(' '))).replace('___', '+')


def getSnippetFn(query):
    """Return the filename to store the snippet file.

    query -- string query

    """
    return join('raw', query + '.html')


def saveSnippet(query, soup):
    """Create HTML file for the query.

    query -- string query
    soup -- HTML soup from beautiful soup

    """
    # Try to identify the minimum HTML to grab
    content = soup.find('div', 'detail_main_wrapper')
    if content is None:
        content = soup.find('div', {'id': 'content'})
    if content is None:
        content = soup
    # Create HTML files in a single directory for organization
    if not isdir('raw'):
        os.makedirs('raw')
    with open(getSnippetFn(query), 'w') as htmlFile:
        htmlFile.write(content.prettify())


def parseTitle(title):
    """Return a standardized Title.

    title -- book title

    """
    if type(title) is str:
        # Remove trailing forward slash and author name
        title = title.split(': a novel /')[0].split(' / ')[0]
        # Remove extra characters in title name
        title = title.replace('electronic resource', '')
        title = title.strip()
    else:
        title = None
    return title


def parseAuthor(author):
    """Return a standardized author name in <first last> format.

    author -- author name

    """
    if type(author) is str:
        # Remove extra characters and words in author name
        author = author.replace('author: ', '').replace(', author.', '')
        author = re.sub(r',\s\d+-', '', author)
        # Reorder author as <first last> from <last, first>
        author = ' '.join([_a.strip() for _a in author.split(',')][::-1])
    else:
        author = None
    return author


def filterBooks(filterKwargs, books):
    """Filter matches books dictionary. Return best matches.

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

    # # Alternative method using difflib to parse matches
    # from difflib import get_close_matches
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


def selectOne(soup, classname):
    """soup.select() wrapper.

    soup -- HTML from beautiful soup
    classname -- class name used filter soup

    """
    # Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class
    selection = soup.select(classname)
    try:
        items = [sel.string.strip() for sel in selection]
        if len(items) == 0:
            return None
        elif len(items) == 1:
            return items[0]
        else:
            print('With `{}`, found: {}'.format(classname, items))
            return '--'.join(items)
    except IndexError:
        return None
