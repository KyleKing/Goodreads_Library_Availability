"""Use bs4 to search the Moco library."""

import json
from difflib import get_close_matches
from html import escape

import requests
from bs4 import BeautifulSoup

base = 'https://mdpl.ent.sirsi.net/client/en_US/catalog/search/results'
kindle = 'qf=ERC_FORMAT%09Electronic+Format%09KINDLE%09KINDLE+%7C%7C+CLOUDLIBRARY+EPUB%09CLOUDLIBRARY+EPUB'

mocoURL = '{}?qu={}&{}'.format(base, '{query}', kindle)


def filterBooks(filterKwargs, books):
    """Filter matches books dictionary. Return up to 3 best matches.

    filterKwargs -- dictionary to compare against the books argument
    books -- list of books with matching keys to the filter args

    """
    idxs = []
    for key in filterKwargs.keys():
        items = [book[key] for book in books if book[key] is not None]
        matches = get_close_matches(filterKwargs[key], items)
        idxs += [items.index(match) for match in matches]
    bestMatches = [books[idx] for n, idx in enumerate(idxs) if idx in idxs[:n]]
    if len(bestMatches) > 0:
        return bestMatches
    else:
        return [books[idx] for idx in list(set(idxs))]


def selectOne(soup_, class_):
    """soup.select() wrapper."""
    # Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class
    sel = soup_.select(class_)
    try:
        return sel[0].string.strip()
    except IndexError:
        return None


def searchLib(title, author='', rawURL=mocoURL):
    """Search the public library for books matching the title and author.

    title -- book title
    author -- (optional) book author
    rawURL -- (optional) URL string that contains '...{query}...'

    """
    query = escape('+'.join(title.split(' ') + author.split(' ')))
    url = rawURL.format(query=query)
    print('Searching with query: {}\nURL:{}'.format(query, url))

    # # FYI: enable pagination
    # page = 0
    # startIdx = page * 12
    # url += '&rw={}'.format(url, startIdx)

    resp = requests.get(url).text
    with open('rawMoco.html', 'w') as outFile:
        outFile.write(resp)

    soup = BeautifulSoup(resp, 'html.parser')

    books = []
    for rIdx, content in enumerate(soup.findAll('div', 'results_bio')):
        books.append({
            'title': content.a['title'].replace('[electronic resource]', '').replace(':', '').strip(),
            'author': selectOne(content, 'div.displayElementText.INITIAL_AUTHOR_SRCH'),
            'format': selectOne(content, 'div.displayElementText.ERC_FORMAT')
        })

    with open('rawBooks.json', 'w') as jsonFile:
        json.dump(books, jsonFile, indent='\t', separators=(',', ': '))

    # Return the best matches from all books returned in search
    return filterBooks({'title': title, 'author': author}, books)


if __name__ == '__main__':
    searchLib('Old Man\'s War')
