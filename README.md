# Goodreads Library Availability

> Check book availability at the Montgomery County Public Library

The app queries the Goodreads API for the authorized user's `To-Read` shelf. The app then iterates through each books and checks if the book is available in the Montgomery Public library digital catalog. This tool could likely be generalized for other public libraries with minor modifications to `gr_lib_sync.moco.searchLib()` and with a custom base url similar to `gr_lib_sync.moco.mocoUrl`.

## Quick Start

If you have Python ^3.6 and the required packages from `poetry.toml` (`rauth` and `beautifulsoup4`). You can run this app with `python goodreads-library-availability.py`

The more reliable way is to install Poetry ([https://github.com/sdispater/poetry](https://github.com/sdispater/poetry#installation)). Then run `poetry install` and `poetry run python goodreads-library-availability.py`.

## Testing

With `poetry` installed. Just run `poetry shell` then `pytest`

### TODO

- Add tests
- Add logging
- Better visualization of CSV output
