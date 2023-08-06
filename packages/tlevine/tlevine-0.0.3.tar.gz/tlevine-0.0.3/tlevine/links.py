import re
import sys
import itertools
import json

import lxml.html
from picklecache import get

def github(username):
    def pages():
        for page_number in itertools.count(1):
            response = get('https://api.github.com/users/%s/repos?page=%d' % (username, page_number))
            yield json.loads(response.text)

    for page in itertools.takewhile(lambda r: r != [], pages()):
        for repository in page:
            yield repository['html_url']

def thomaslevine():
    url = 'http://thomaslevine.com/!/'
    response = get(url)
    html = lxml.html.fromstring(response.text)
    html.make_links_absolute(url)
    return (str(link) for link in html.xpath('//a/@href') if link.startswith(url))

def scraperwiki(url = 'https://classic.scraperwiki.com/profiles/tlevine/index.html'):
    response = get(url)
    html = lxml.html.fromstring(response.text)
    html.make_links_absolute(url)
    for href in html.xpath('//li[@class="code_object_line"]/descendant::h3/a[position()=2]/@href'):
        yield re.sub(r'index.html$', '', str(href))
    nexts = html.xpath('//a[text()="Next »"]/@href')
    if nexts != []:
        yield from scraperwiki(nexts[0])

def gitorious():
    url = 'https://gitorious.org/tlevine.xml'
    response = get(url)
    project = lxml.html.fromstring(response.text.encode('utf-8'))
    project.make_links_absolute(url)
    for repository in project.xpath('//repository[owner[text()="tlevine"]]'):
        yield 'https' + repository.xpath('clone_url/text()')[0][3:-4]

def manual():
    return [
        'https://pypi.python.org/pypi/blizzard',
        'https://pypi.python.org/pypi/bugs-everywhere',
        'https://pypi.python.org/pypi/cereal_jar',
        'https://pypi.python.org/pypi/craigsgenerator',
        'https://pypi.python.org/pypi/ddpy',
        'https://pypi.python.org/pypi/dicti',
        'https://pypi.python.org/pypi/download_ckan',
        'https://pypi.python.org/pypi/download_junar',
        'https://pypi.python.org/pypi/download_opendataphilly',
        'https://pypi.python.org/pypi/download_opendatasoft',
        'https://pypi.python.org/pypi/download_socrata',
        'https://pypi.python.org/pypi/dumptruck',
        'https://pypi.python.org/pypi/get-cached',
        'https://pypi.python.org/pypi/juliadown',
        'https://pypi.python.org/pypi/jumble',
        'https://pypi.python.org/pypi/mailfest-scoreboard',
        'https://pypi.python.org/pypi/picklecache',
        'https://pypi.python.org/pypi/pickle-warehouse',
        'https://pypi.python.org/pypi/randomsleep',
        'https://pypi.python.org/pypi/scarsdale-property-inquiry',
        'https://pypi.python.org/pypi/scraperwiki_local',
        'https://pypi.python.org/pypi/sheetmusic',
        'https://pypi.python.org/pypi/sliding_window',
        'https://pypi.python.org/pypi/socrata',
        'https://pypi.python.org/pypi/special_snowflake',
        'https://pypi.python.org/pypi/tlevine',
        'https://pypi.python.org/pypi/to_function',
        'https://pypi.python.org/pypi/treasuryio',
        'https://chrome.google.com/webstore/detail/simple-webcam/cejgmnpegppdhkmmgmdobfelcdgfhkmo?hl=en',
    ]

def main():
    iter_github = list(map(github, ['tlevine', 'csv', 'csvsoundsystem', 'appgen', 'risley', 'mapshit']))
    iter_other  = [gitorious(), scraperwiki(), thomaslevine(), manual()]
    args = iter_other + iter_github
    for link in itertools.chain(*args):
        try:
            sys.stdout.write('%s\n' % link)
        except BrokenPipeError:
            break
