"""Core gr_lib_sync/ functionality."""

from .moco import searchLib
from .toRead import clearCache, downloadGRShelf


def run(fresh=False):
    """Read books from Goodreads shelf, then check availability in library.

    fresh -- (optional) if False, use locally cached files

    """
    if fresh:
        clearCache()
    downloadGRShelf()

    # TODO: Loop each book from Goodreads
    searchLib('old man\'s war')


if __name__ == '__main__':
    run()
