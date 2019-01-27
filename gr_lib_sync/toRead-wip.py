"""Goodreads API Demo"""
# Based on: https://www.goodreads.com/api/oauth_example#python
# Also see: https://gist.github.com/gpiancastelli/537923
#  & https://gist.github.com/5862716.git

import csv
import json
import time
import xml.etree.ElementTree as ET
from glob import iglob
from os import getcwd, makedirs
from os.path import isdir, isfile, join

from rauth.service import OAuth1Service, OAuth1Session

# Init Environment
envFn = '.env.json'


def updateEnv(_env):
    # Update environment file with latest
    with open(envFn, 'w') as envFile:
        json.dump(_env, envFile)


if not isfile(envFn):
    # Initialize environment file if one does not exist. DO NOT CHECK THIS INTO a VCS :)
    data = {'CONSUMER_KEY': 'TBD', 'CONSUMER_SECRET': 'TBD'}
    updateEnv(data)
# Read environment file
with open(envFn) as envFile:
    env = json.load(envFile)

# if response.status_code != 201:
#     raise RuntimeError('Cannot create resource: %s' % response.status_code)
# else:
#     print('Book added!')

# ====================================================================================================================

if env['CONSUMER_KEY'] == 'TBD':
    errMsg = """No CONSUMER_KEY or CONSUMER_SECRET in `{envFn}`
Get your Goodreads consumer key & secret from: https://www.goodreads.com/api/keys
In `{envFn}`, replace `TBD` with the correct key
""".format(envFn=envFn)
    raise RuntimeError(errMsg)

goodreads = OAuth1Service(
    consumer_key=env['CONSUMER_KEY'],
    consumer_secret=env['CONSUMER_SECRET'],
    name='goodreads',
    request_token_url='https://www.goodreads.com/oauth/request_token',
    authorize_url='https://www.goodreads.com/oauth/authorize',
    access_token_url='https://www.goodreads.com/oauth/access_token',
    base_url='https://www.goodreads.com/'
)

if 'request_token_secret' not in env:
    # head_auth=True is important here; this doesn't work with oauth2 for some reason
    env['request_token'], env['request_token_secret'] = goodreads.get_request_token(header_auth=True)
    print('token:{}\nsecret:{}'.format(env['request_token'], env['request_token_secret']))

    authorize_url = goodreads.get_authorize_url(env['request_token'])
    print('Visit this URL in your browser: ' + authorize_url)
    resp = ''
    while resp.lower() != '':
        # you need to access the authorize_link via a browser,
        # and proceed to manually authorize the consumer
        resp = input('Have you authorized me? (y/n) ')
    if resp != 'y':
        raise RuntimeError('Response `{}` was not "y"'.format(resp))

    updateEnv(env)
    time.sleep(1)  # Sleep to prevent too many GR requests

if 'ACCESS_TOKEN_SECRET' not in env:
    session = goodreads.get_auth_session(env['request_token'], env['request_token_secret'])

    # these values are what you need to save for subsequent access.
    env['ACCESS_TOKEN'] = session.access_token
    env['ACCESS_TOKEN_SECRET'] = session.access_token_secret
    print('ACCESS_TOKEN:{}\n ACCESS_TOKEN_SECRET:{}'.format(env['ACCESS_TOKEN'], env['ACCESS_TOKEN_SECRET']))
    updateEnv(env)
    time.sleep(1)  # Sleep to prevent too many GR requests

# ====================================================================================================================
# Get books from reading list:
# https://www.goodreads.com/review/list/71014262.xml
#     v: 2
#     id: Goodreads id of the user
#     shelf: read, currently-reading, to-read, etc. (optional)
#     sort: title, author, cover, rating, year_pub, date_pub, date_pub_edition, date_started, date_read, date_updated,
#       date_added, recommender, avg_rating, num_ratings, review, read_count, votes, random, comments, notes, isbn,
#       isbn13, asin, num_pages, format, position, shelves, owned, date_purchased, purchase_location,
#       condition (optional)
#     search[query]: query text to match against member's books (optional)
#     order: a, d (optional)
#     page: 1-N (optional)
#     per_page: 1-200 (optional)
#     key: Developer key (required).

new_session = OAuth1Session(
    consumer_key=env['CONSUMER_KEY'],
    consumer_secret=env['CONSUMER_SECRET'],
    access_token=env['ACCESS_TOKEN'],
    access_token_secret=env['ACCESS_TOKEN_SECRET'],
)

if 'user_id' not in env:
    # TODO: Use this to get the user_id
    response = new_session.get('https://www.goodreads.com/api/auth_user')
    print(response.text)
    root = ET.fromstring(response.text)
    env['user_id'] = root.find('user_id').text
    updateEnv(env)
    time.sleep(1)  # Sleep to prevent too many GR requests

# ====================================================================================================================

page = 0
xmlDir = join(getcwd(), 'XML-{}'.format(env['user_id']))
if not isdir(xmlDir):
    makedirs(xmlDir)
while page is not None:
    page += 1
    xmlFn = join(xmlDir, 'gr-raw-{:02d}.xml'.format(page))
    if not isfile(xmlFn):
        print('Querying page: {}'.format(page))
        data = {
            'v': 2,
            'id': env['user_id'],
            'shelf': 'to-read',
            'sort': 'avg_rating',
            'order': 'd',
            'page': page,
            'per_page': 30
        }
        response = new_session.post('https://www.goodreads.com/review/list/71014262.xml', data)

        root = ET.fromstring(response.text)
        if all([int(root.find('reviews').attrib[key]) != 0 for key in ['start', 'end']]):  # TOTAL
            with open(xmlFn, 'w') as outFile:
                outFile.write(response.text)
            time.sleep(1)  # Sleep to prevent too many GR requests
        else:
            print('Found all book from reading list\n')
            page = None

legend = [
    'id', 'isbn', 'isbn13', 'text_reviews_count', 'title', 'title_without_series', 'image_url', 'link',
    'num_pages', 'average_rating', 'ratings_count', 'published'
]
csvFn = join(getcwd(), 'gr-parsed.csv')
print('Creating CSV File summary at: {}'.format(csvFn))
with open(csvFn, 'w') as csvFile:
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(legend)
    for xmlFn in iglob(join(xmlDir, '*')):
        root = ET.parse(xmlFn).getroot()
        for child in root.iter('book'):
            # for kid in child:
            #     print(kid.tag, kid.attrib, kid.text)
            csvWriter.writerow([child.find(key).text for key in legend])
