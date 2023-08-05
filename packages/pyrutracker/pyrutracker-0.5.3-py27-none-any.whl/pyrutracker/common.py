#!/usr/bin/env python
# coding=utf-8

from collections import namedtuple, OrderedDict
import urllib
import urlparse
import re
import string
from datetime import datetime

import bs4

RUTRACKER_URL = "http://rutracker.org/forum/index.php"
PAGE_SIZE = 50
PATTERN = r"^([^:?!()]+)[\s]*:([^\n]+)"
MONTHES = {u'Янв': '01', u'Фев': '02', u'Мар': '03', u'Апр': '04',
           u'Май': '05', u'Июн': '06', u'Июл': '07', u'Авг': '08',
           u'Сен': '09', u'Окт': '10', u'Ноя': '11', u'Дек': '12'}

Category = namedtuple('Category', ['title', 'subforums'])
Subforum = namedtuple('Subforum', ['title', 'date', 'url', 'headers'])
Topic = namedtuple('Topic',
                   ['size', 'title', 'date',
                    'get_description', 'url', 'headers'])


class PageBlocked(Exception):
    """Exception for blocked pages"""
    def __init__(self, *arg, **kwd):
        super(PageBlocked, self).__init__(*arg, **kwd)


def clear_text(text):
    """returns text with utf-8 encoding and whithout trailing whitespaces"""
    # return text.encode('utf-8').strip(string.whitespace)
    return text.strip(string.whitespace)


def is_blocked(doc):
    """return True if page is blocked otherwise False"""
    try:
        return doc.find('body').div.get('class')[0] == 'msg'
    except (TypeError, IndexError):
        return False


def html_from_url(url, exception_if_blocked=True):
    """return BeautifulSoup instance from url
    Args:
        exception_if_blocked - raise PageBlocked exception for blocked pages
    """
    doc = bs4.BeautifulSoup(urllib.urlopen(url).read())
    if exception_if_blocked and is_blocked(doc):
        raise PageBlocked(url)
    else:
        return doc


def categories(doc):
    """ returns forum's categories as an iterable object
        with Category namedtuple members
    """
    for el in doc.select('div.category h3.cat_title'):
        yield Category(clear_text(el.text), subforums(el.parent.table))


def pages(doc):
    """returns iterable pages' urls"""
    try:
        nav_p = doc.select('#pagination a.menu-root')[0].parent
    except IndexError:
        short_url = doc.select("td.nav-top")[0].find_all('a')[-1].get('href')
        url = urlparse.urljoin(RUTRACKER_URL, short_url)
        yield url
        raise StopIteration
    # the first element is a.menu-root - menu container
    first_page = 1
    try:
        last_page = int(clear_text(nav_p.find_all(["a", "b"])[-1].text))
    except ValueError:
        last_page = int(clear_text(nav_p.find_all(["a", "b"])[-2].text))
    url = nav_p.find_all('a')[-1].get('href')
    link = urlparse.urljoin(RUTRACKER_URL, re.sub(r"&start=\d+", "", url))
    current_page = first_page
    while current_page <= last_page:
        yield "{0}&start={1}".format(link, PAGE_SIZE * (current_page - 1))
        current_page += 1


def get_headers(doc):
    """ returns headers(categories) as a tuple """
    headers_el = doc.select('#main_content_wrap td.nav a')[1:]
    return tuple(map(clear_text, (el.text for el in headers_el)))


def subforums(doc):
    """ return subforums items """
    headers = get_headers(doc)
    for el in doc.select('h4.forumlink'):
        link = urlparse.urljoin(RUTRACKER_URL, el.a.get('href'))
        # parse date and time info
        try:
            date_descr = clear_text(
                el.find_parent('tr').find_all('td')[-1].p.text)
            date = date_descr[:15]
            for name, index in MONTHES.items():
                date = date.replace(name, index)
            date = datetime.strptime(date.encode('utf-8'), '%d-%m-%y %H:%M')
        except (ValueError, AttributeError):
            date = None
        yield Subforum(title=clear_text(el.text), date=date,
                       url=link, headers=headers)


def topics(doc):
    """ return topics as a iterable object of Topic namedtuple """
    headers = get_headers(doc)
    for el in doc.select('table tr.hl-tr a.topictitle'):
        cols = el.find_parent('tr').find_all('td')
        size = clear_text(cols[2].text)
        date = clear_text(cols[-1].p.text)
        date = datetime.strptime(date, '%Y-%m-%d %H:%M')
        if not size or 'b' not in size.lower():
            continue
        link = urlparse.urljoin(RUTRACKER_URL, el.get('href'))
        fn = lambda: topic_description(html_from_url(link))
        yield Topic(title=clear_text(el.text),
                    size=size, date=date, get_description=fn,
                    url=link, headers=headers)


def page_items(doc):
    """ return page items: Subforum or Topic """
    for subforum in subforums(doc):
        yield subforum

    for topic in topics(doc):
        yield topic


def _topic_text(doc):
    """ return topic text """
    topic = bs4.BeautifulSoup(str(doc))
    for el in topic.select('.sp-wrap'):
        el.decompose()
    for el in (topic.select('.post-br') +
               topic.select('.post-hr') +
               topic.find_all('br')
               ):
        el.string = '\n\n'

    post_body = topic.select('div.post_body')[0]
    return clear_text(post_body.get_text())


def topic_description(doc):
    """ return topic description as an OrderedDict """
    text = _topic_text(doc)
    result = OrderedDict()
    key, value = None, None
    lines = text.split('\n')
    result[u'Название'] = lines[0]
    for line in lines:
        line = clear_text(line).lstrip(string.punctuation)
        m = re.match(PATTERN, line)
        if (m and value) or (not line and value):
            result[key] = clear_text(value)
            key = value = None
        if m:
            key, value = m.group(1), m.group(2)
        elif value:
            value = value + "\n" + line
    return result


def next_page(doc):
    try:
        nav_p = doc.select('#pagination a.menu-root')[0].parent
        short_url = nav_p.find_all(['a', 'b'])[-1].get('href')
        if short_url:
            return urlparse.urljoin(RUTRACKER_URL, short_url)
    except IndexError:
        return None
