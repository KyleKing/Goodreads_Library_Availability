"""Core gr_lib_sync/ functionality."""

import csv

from .moco import searchLib
from .toRead import clearCache, downloadGRShelf, listBooks

csvFn = 'library-summary.csv'


def run(fresh=False):
    """Read books from Goodreads shelf, then check availability in library.

    fresh -- (optional) if False, use locally cached files

    """
    if fresh:
        clearCache()
    downloadGRShelf()

    legend = [
        'Title', 'Author', 'Rating', 'Lib-Format', 'Lib-Title', 'Lib-Author'
    ]
    print('Creating CSV Library Summary: {}'.format(csvFn))
    with open(csvFn, 'w') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(legend + ['author'])
        for bIdx, book in enumerate(listBooks()):
            row = [book['title'], book['author'], book['rating']]
            for match in searchLib(book['title'], book['author']):
                row.extend([match['format'], match['title'], match['author']])
            csvWriter.writerow(row)

            if bIdx >= 29:
                break


if __name__ == '__main__':
    run()
