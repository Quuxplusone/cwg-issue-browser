#!/usr/bin/env python

import bottle
from bottle import Bottle
import os
import re
import requests
import time


app = Bottle()
bottle.TEMPLATE_PATH.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'views'))


class NoSuchIssueException(Exception):
    def __init__(self, n):
        self.issue_number = n


class UpstreamNotParseableException(Exception):
    def __init__(self, r, url):
        self.r = r
        self.status_code = r.status_code
        self.text = r.text
        self.url = url


class UpstreamUnreachableException(Exception):
    def __init__(self, r, url):
        self.r = r
        self.status_code = r.status_code
        self.text = r.text
        self.url = url


def get_full_cwg_page(url):
    r = requests.get(url)
    text = r.text
    if r.status_code != 200:
        raise UpstreamUnreachableException(r, url)
    if not text.startswith('<HTML>'):
        raise UpstreamNotParseableException(r, url)
    return text


def get_snippet(page_text, issue_id):
    anchor_tag = '<A NAME="%s">' % issue_id
    try:
        start_idx = page_text.index(anchor_tag)
    except ValueError:
        raise NoSuchIssueException(issue_id)
    try:
        end_idx = page_text.index('<A NAME="', start_idx + 1)
    except ValueError:
        end_idx = len(page_text)
    return page_text[start_idx:end_idx]


class Issue:
    def __init__(self, status, text):
        self.status = status
        self.text = text


class PageCache:
    def __init__(self, urls):
        self.issues = {}       # str(id) -> Issue
        self.url_sizes = {}    # str(url) -> int
        self.last_fetch_time = 0
        self.urls = urls

    def refresh(self):
        for url in self.urls:
            status = 'active' if 'active' in url else 'closed' if 'closed' in url else 'defect'
            try:
                page_text = get_full_cwg_page(url)
                self.url_sizes[url] = len(page_text)
                issue_ids = [m.group(1) for m in re.finditer(r'<A NAME="(\d+)">', page_text)]
                for issue_id in issue_ids:
                    self.issues[issue_id] = Issue(status, get_snippet(page_text, issue_id))
            except UpstreamUnreachableException:
                pass
        self.last_fetch_time = time.time()

    def maybe_refresh(self):
        if time.time() - self.last_fetch_time >= 3600:
            self.refresh()

    def get_issue(self, issue_id):
        issue = self.issues.get(issue_id)
        if issue is None:
            raise NoSuchIssueException(issue_id)
        return issue

    def get_issues_and_statuses(self):
        result = list(self.issues.keys())
        result.sort(key=int)
        return [(issue_id, self.issues[issue_id].status) for issue_id in result]

    def to_human_readable(self, page_size):
        if page_size < 10000:
            return '%d bytes' % page_size
        elif page_size < 10000000:
            return '%d KB' % (page_size / 1000)
        elif page_size < 10000000000:
            return '%d MB' % (page_size / 1000000)
        else:
            return '%d GB' % (page_size / 1000000000)

    def get_urls_and_sizes(self):
        return [
            (url, self.to_human_readable(size))
            for url, size in self.url_sizes.items()
        ]


gPageCache = PageCache([
    'http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_active.html',
    'http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_closed.html',
    'http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_defects.html',
])


@app.get('/robots.txt')
def robots_txt():
    bottle.response.content_type = 'text/plain'
    return 'User-agent: *\nDisallow: /\n'


@app.get('/')
@app.get('/index.html')
def home():
    gPageCache.maybe_refresh()
    return bottle.template('index.tpl', {
        'urls_and_sizes': gPageCache.get_urls_and_sizes(),
        'issues_and_statuses': gPageCache.get_issues_and_statuses(),
    })


@app.get('/<cwgn:re:cwg[0-9]+>')
def issue_page(cwgn):
    gPageCache.maybe_refresh()
    issue_id = cwgn[3:]
    try:
        issue = gPageCache.get_issue(issue_id)
        return bottle.template('issue.tpl', {
            'issue_id': issue_id,
            'issue_text': issue.text,
            'status': issue.status,
        })
    except NoSuchIssueException as ex:
        return bottle.template('nosuchissue.tpl', {
            'issue_number': ex.issue_number,
        })
    except UpstreamNotParseableException as ex:
        return bottle.template('upstreamnotparseable.tpl', {
            'status_code': ex.status_code,
            'text': ex.text[:1000],
            'url': ex.url,
        })
    except UpstreamUnreachableException as ex:
        return bottle.template('upstreamunreachable.tpl', {
            'status_code': ex.status_code,
            'text': ex.text[:1000],
            'url': ex.url,
        })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
