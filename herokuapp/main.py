#!/usr/bin/env python

import bottle
from bottle import Bottle
import os
import requests
import time


app = Bottle()
bottle.TEMPLATE_PATH.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'views'))

FULL_CWG_PAGE_URL = 'http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_defects.html'


class NoSuchIssueException(Exception):
    def __init__(self, n):
        self.issue_number = n


class UpstreamNotParseableException(Exception):
    def __init__(self, r):
        self.r = r
        self.status_code = r.status_code
        self.text = r.text


class UpstreamUnreachableException(Exception):
    def __init__(self, r):
        self.r = r
        self.status_code = r.status_code
        self.text = r.text


def get_full_cwg_page():
    r = requests.get(FULL_CWG_PAGE_URL)
    text = r.text
    if r.status_code != 200:
        raise UpstreamUnreachableException(r)
    if not text.startswith('<HTML>'):
        raise UpstreamNotParseableException(r)
    return text


cached_text = None
cached_time = None
def get_full_cwg_page_from_cache():
    global cached_text
    global cached_time
    now = time.time()
    if cached_text is None:
        cached_text = get_full_cwg_page()
        cached_time = now
    elif (now - cached_time) >= 3600:
        try:
            cached_text = get_full_cwg_page()
            cached_time = now
        except UpstreamUnreachableException:
            pass
    return cached_text


def get_snippet(n):
    page_text = get_full_cwg_page_from_cache()
    anchor_tag = '<A NAME="%d">' % n
    try:
        start_idx = page_text.index(anchor_tag)
    except ValueError:
        raise NoSuchIssueException(n)
    try:
        end_idx = page_text.index('<A NAME="', start_idx + 1)
    except ValueError:
        end_idx = len(page_text)
    return page_text[start_idx:end_idx]


@app.get('/robots.txt')
def robots_txt():
    bottle.response.content_type = 'text/plain'
    return 'User-agent: *\nDisallow: /\n'


@app.get('/')
@app.get('/index.html')
def home():
    return bottle.static_file('index.html', root='./herokuapp/static', mimetype='text/html')


@app.get('/<cwgn:re:cwg[0-9]+>')
def issue_page(cwgn):
    n = int(cwgn[3:])
    try:
        snippet = get_snippet(n)
        bottle.response.content_type = 'text/html'
        return '<html><head><title>CWG%d (issue browser)</title></head><body>%s</body></html>' % (n, snippet)
    except NoSuchIssueException as ex:
        return bottle.template('nosuchissue.tpl', {
            'issue_number': ex.issue_number,
            'url': FULL_CWG_PAGE_URL,
        })
    except UpstreamNotParseableException as ex:
        return bottle.template('upstreamnotparseable.tpl', {
            'status_code': ex.status_code,
            'text': ex.text[:1000],
            'url': FULL_CWG_PAGE_URL,
        })
    except UpstreamUnreachableException as ex:
        return bottle.template('upstreamunreachable.tpl', {
            'status_code': ex.status_code,
            'text': ex.text[:1000],
            'url': FULL_CWG_PAGE_URL,
        })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
