"""Download CSV Summary of Goodreads To-Read Shelf."""
# Based on: https://www.goodreads.com/api/oauth_example#python
# Also see: https://gist.github.com/gpiancastelli/537923
#  & https://gist.github.com/5862716.git

import csv
import json
import time
import webbrowser
import xml.etree.ElementTree as ET
from glob import iglob
from os import makedirs
from os.path import isdir, isfile, join
from shutil import rmtree

from rauth.service import OAuth1Service, OAuth1Session

# Use local JSON file to store user-specific keys
envFn = '.env.json'
csvFn = 'goodreads-summary.csv'
xmlDir = 'RawGoodreadsXML'

# Standardize env JSON key names
CONSUMER_KEY = 'CONSUMER_KEY'
CONSUMER_SECRET = 'CONSUMER_SECRET'
REQ_TOKEN_SECRET = 'REQ_TOKEN_SECRET'
ACCESS_TOKEN = 'ACCESS_TOKEN'
ACCESS_TOKEN_SECRET = 'ACCESS_TOKEN_SECRET'
USER_ID = 'user_id'


def updateEnv(_env):
    """Backup environment to local file.

    _env -- environment JSON dictionary

    """
    with open(envFn, 'w') as envFile:
        json.dump(_env, envFile, indent='\t', separators=(',', ': '))


def loadEnv():
    """Read environment from local file."""
    if not isfile(envFn):
        # Initialize environment file if one does not exist
        data = {CONSUMER_KEY: 'TBD', CONSUMER_SECRET: 'TBD'}
        updateEnv(data)
    with open(envFn) as envFile:
        return json.load(envFile)


def clearCache():
    """Clear the XML directory."""
    if isdir(xmlDir):
        rmtree(xmlDir)


def downloadGRShelf():
    """Create a CSV summary of all books on a users' Goodreads To-Read list."""
    env = loadEnv()

    # Verify consumer key exists in environment
    if env[CONSUMER_KEY] == 'TBD':
        errMsg = """No CONSUMER_KEY or CONSUMER_SECRET in `{envFn}`
    Get your Goodreads consumer key & secret from: https://www.goodreads.com/api/keys
    In `{envFn}`, replace `TBD` with the correct key
    """.format(envFn=envFn)
        raise RuntimeError(errMsg)

    goodreads = OAuth1Service(
        consumer_key=env[CONSUMER_KEY],
        consumer_secret=env[CONSUMER_SECRET],
        name='goodreads',
        request_token_url='https://www.goodreads.com/oauth/request_token',
        authorize_url='https://www.goodreads.com/oauth/authorize',
        access_token_url='https://www.goodreads.com/oauth/access_token',
        base_url='https://www.goodreads.com/'
    )

    # Fetch the request tokens for a new authorized session
    if REQ_TOKEN_SECRET not in env:
        env['REQ_TOKEN'], env[REQ_TOKEN_SECRET] = goodreads.get_request_token(header_auth=True)
        print('token:{}\nsecret:{}'.format(env['REQ_TOKEN'], env[REQ_TOKEN_SECRET]))

        authURL = goodreads.get_authorize_url(env['REQ_TOKEN'])
        print('\nVisit this URL in your browser: ' + authURL)
        webbrowser.open_new(authURL)
        resp = input('Have you authorized me? (y/n) ')
        if resp != 'y':
            raise RuntimeError('Response `{}` was not "y"'.format(resp))

        updateEnv(env)
        time.sleep(1)  # Sleep to prevent too many GR requests

    # Get ACCESS Token Keys
    if ACCESS_TOKEN_SECRET not in env:
        session = goodreads.get_auth_session(env['REQ_TOKEN'], env[REQ_TOKEN_SECRET])
        env[ACCESS_TOKEN] = session.access_token
        env[ACCESS_TOKEN_SECRET] = session.access_token_secret
        print('ACCESS_TOKEN:{}\n ACCESS_TOKEN_SECRET:{}'.format(env[ACCESS_TOKEN], env[ACCESS_TOKEN_SECRET]))
        updateEnv(env)
        time.sleep(1)  # Sleep to prevent too many GR requests

    # Create new session with ACCESS Tokens
    newSession = OAuth1Session(
        consumer_key=env[CONSUMER_KEY],
        consumer_secret=env[CONSUMER_SECRET],
        access_token=env[ACCESS_TOKEN],
        access_token_secret=env[ACCESS_TOKEN_SECRET]
    )

    # Get user id for user who authorized the session
    if USER_ID not in env:
        response = newSession.get('https://www.goodreads.com/api/auth_user')
        root = ET.fromstring(response.text)
        env[USER_ID] = root.find('user').attrib['id']
        updateEnv(env)
        time.sleep(1)  # Sleep to prevent too many GR requests

    # ====================================================================================================================
    # Get books from reading list:
    # https://www.goodreads.com/review/list/71014262.xml
    #     v: 2
    #     id: Goodreads id of the user
    #     shelf: read, currently-reading, to-read, etc. (optional)
    #     sort: title, author, rating, year_pub, date_updated, date_added, avg_rating, num_ratings,
    #           review, votes, num_pages...
    #     search[query]: query text to match against member's books (optional)
    #     order: a, d (optional)
    #     page: 1-N (optional)
    #     per_page: 1-200 (optional)
    #     key: Developer key (required).

    page = 0
    if not isdir(xmlDir):
        makedirs(xmlDir)
    while page is not None:
        page += 1
        xmlFn = join(xmlDir, 'gr-raw-{:02d}.xml'.format(page))
        if not isfile(xmlFn):
            print('Querying page: {}'.format(page))
            data = {
                'v': 2,
                'id': env[USER_ID],
                'shelf': 'to-read',
                'sort': 'avg_rating',
                'order': 'd',
                'page': page,
                'per_page': 30
            }
            response = newSession.post('https://www.goodreads.com/review/list/71014262.xml', data)

            root = ET.fromstring(response.text)
            if all([int(root.find('reviews').attrib[key]) != 0 for key in ['start', 'end']]):  # TOTAL
                with open(xmlFn, 'w') as outFile:
                    outFile.write(response.text)
                time.sleep(1)  # Sleep to prevent too many GR requests
            else:
                print('Found all books in reading list\n')
                page = None

    legend = [
        'id', 'isbn', 'isbn13', 'text_reviews_count', 'title', 'title_without_series', 'image_url', 'link',
        'num_pages', 'average_rating', 'ratings_count', 'published'
    ]
    print('Creating CSV File summary: {}'.format(csvFn))
    with open(csvFn, 'w') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(legend + ['author'])
        for xmlFn in iglob(join(xmlDir, '*')):
            root = ET.parse(xmlFn).getroot()
            for child in root.iter('book'):
                # for kid in child:
                #     print(kid.tag, kid.attrib, kid.text)
                row = [child.find(key).text for key in legend]
                for author in child.iter('author'):
                    row.append(author.find('name').text)
                csvWriter.writerow(row)


def listBooks():
    """Return list of books"""
    books = []
    with open(csvFn, 'r') as csvFile:
        for idx, row in enumerate(csv.reader(csvFile)):
            if idx == 0:
                legend = row
            else:
                books.append({
                    'title': row[legend.index('title_without_series')],
                    'author': row[legend.index('author')],
                    'rating': row[legend.index('average_rating')]
                })
    return books


if __name__ == '__main__':
    downloadGRShelf()
