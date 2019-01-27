from os.path import isfile

import requests
from bs4 import BeautifulSoup


def selectOne(soup_, class_):
    """Wrapper for soup.select()
        Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#searching-by-css-class
    """
    return soup_.select(class_)[0].string.strip()


# TODO: HTML Encode
query = 'old man%27s war'

for page in range(3):
    startIdx = page * 12

    base = 'https://mdpl.ent.sirsi.net/client/en_US/catalog/search/results'
    kindle = 'qf=ERC_FORMAT%09Electronic+Format%09KINDLE%09KINDLE+%7C%7C+CLOUDLIBRARY+EPUB%09CLOUDLIBRARY+EPUB'

    url = '{}?qu={}&{}&rw={}'.format(base, '+'.join(query.split(' ')), kindle, startIdx)

    print('\n{}\nURL: {}'.format('=' * 80, url))

    outFn = 'demo-{}.html'.format(page)
    if not isfile(outFn):
        data = requests.get(url).text
        with open(outFn, 'w') as outFile:
            outFile.write(data)

    with open(outFn, 'r') as outFile:
        soup = BeautifulSoup(outFile, 'html.parser')

    for rIdx, content in enumerate(soup.findAll('div', 'results_bio')):
        print('\n------ {:02d} ------'.format(rIdx))
        print(' >Title:\n   {}'.format(content.a['title'].strip()))
        for key in ['INITIAL_AUTHOR_SRCH', 'ERC_FORMAT', 'Excerpt']:
            # content.find_all('div', key)[1].string
            # content.select('div.displayElementText.{}'.format(key))[0].string
            print(' >{}:\n   {}'.format(key, selectOne(content, 'div.displayElementText.' + key)))
