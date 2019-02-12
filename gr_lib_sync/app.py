"""Core gr_lib_sync/ functionality."""

import random

import jsonlines

from .moco import searchLib
from .toRead import clearCache, downloadGRShelf, listBooks

jsonlFn = 'library-summary.jsonl'


def run(fresh=False):
    """Read books from Goodreads shelf, then check availability in library.

    fresh -- (optional) if False, use locally cached files

    """
    if fresh:
        clearCache()
    downloadGRShelf()

    print('Creating Library Summary: {}'.format(jsonlFn))

    with jsonlines.open(jsonlFn, 'w') as jWriter:
        for bIdx, book in enumerate(listBooks()):
            book['idx'] = bIdx
            book['libMatches'], url = searchLib(book['title'], book['author'])
            book['tComps'] = {'title': book['title'], 'link': url}
            countSum = 0
            for key in ['kindle', 'eResource', 'physical', 'audio']:
                book[key] = len([True for _m in book['libMatches'] if _m[key]])
                countSum += book[key]
            book['unknown'] = len(book['libMatches']) - countSum
            book['random'] = random.randrange(100) / 10.0

            jWriter.write(book)
            if bIdx >= 200:  # FYI: Debugging only
                break
    # Format the jsonlines file as JavaScript to be read natively by the Web App
    with open(jsonlFn, 'r') as jlFile:
        with open('web_app/{}.js'.format(jsonlFn.split('.')[0]), 'w') as jsFile:
            jsFile.write('var aggBooks = [{}]'.format(',\n'.join(jlFile.read().splitlines())))


if __name__ == '__main__':
    run()
