# Goodreads Library Availability

> Check book availability at the Montgomery County Public Library

The app queries the Goodreads API for the authorized user's `To-Read` shelf.

The app then checks each book for availability in the Montgomery Public library digital catalog.

The result is a CSV summary of all books in the user's To-Read Goodreads shelf (`goodreads-summary.csv`) and a CSV summary of the books and library availability (`library-summary.csv`). I plan to make better output, but for now just open the CSV in R, Numbers, or Excel.

Initially I wanted to use the Overdrive API, but they don't provide access for personal projects. This tool could likely be generalized for other public libraries with minor modifications to `gr_lib_sync.moco.searchLib()` and with a custom base url similar to `gr_lib_sync.moco.mocoUrl`.

Open an issue if you have a different library to search.

## Quick Start

If you have Python ^3.6 and the required packages from `poetry.toml` (`rauth`, `beautifulsoup4`, etc.). You can run this app with `python main.py`

The more reliable way is to install Poetry ([https://github.com/sdispater/poetry](https://github.com/sdispater/poetry#installation)). Then run `poetry install` and `poetry run python main.py`.

## Testing

With `poetry` installed, run `poetry shell` then `pytest` or `pytest -l -x`.
