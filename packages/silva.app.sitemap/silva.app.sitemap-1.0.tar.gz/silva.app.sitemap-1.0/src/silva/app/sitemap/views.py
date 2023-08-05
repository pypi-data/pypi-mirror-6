# -*- coding: utf-8 -*-
# Copyright (c) 2012 Infrae. All rights reserved.
# See also LICENSE.txt

from xml.sax.saxutils import escape
from itertools import imap, ifilter

from five import grok
from zope.component import getUtility, queryUtility
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.publisher.interfaces.http import IResult

from zExceptions import NotFound

from silva.core.interfaces import IContainer
from silva.core.services.interfaces import ICatalogService

from .interfaces import ISitemapService


class BufferedGeneratorStream(object):
    grok.implements(IResult)

    def __init__(self, generator, size=200 * 1024, encoding='utf-8'):
        self.generator = generator
        self.encoding = encoding
        self._buffer = bytearray(size)
        self._cursor = 0
        self._size = size
        self._done = False

    def __iter__(self):
        return self

    def next(self):
        if self._done:
            raise StopIteration

        try:
            remaining = ''
            while self._cursor < self._size:
                item = self.generator.next().encode(self.encoding)
                remaining_len = self._size - self._cursor
                if len(item) > remaining_len:
                    remaining = item
                    break
                next_pos = self._cursor + len(item)
                self._buffer[self._cursor:next_pos] = item
                self._cursor = next_pos

            result = str(self._buffer[:self._cursor]) + remaining
            self._cursor = 0
            return result
        except StopIteration:
            self._done = True
            if self._cursor:
                return str(self._buffer[:self._cursor])
            raise StopIteration


def _normalized_path(p):
    return p.endswith('/') and p or p + '/'

def _utf8_encode(s):
    return s.encode('utf-8')


class SitemapView(grok.View):
    grok.context(IContainer)
    grok.name('sitemap.xml')

    def update(self):
        self.sitemap = queryUtility(ISitemapService)
        if self.sitemap is None:
            raise NotFound()
        catalog = getUtility(ICatalogService)
        query = dict(
            path=map(_utf8_encode, self.sitemap.get_paths()),
            publication_status="public",
            meta_type=map(_utf8_encode, self.sitemap.get_allowed_meta_types())
        )
        brains = catalog.search(query)
        self.trim_index = self.sitemap.get_trim_index()
        self.seen = set()
        self.excluded_paths = map(_normalized_path,
            self.sitemap.get_excluded_paths())

        pipe = iter(brains)
        pipe = ifilter(self.has_date, pipe)
        pipe = ifilter(self.exclude, pipe)
        pipe = imap(self.process, pipe)
        pipe = ifilter(self.dedup, pipe)
        self.pipe = pipe

    def exclude(self, brain):
        return not self.sitemap.is_path_excluded(brain.getPath().split('/'))

    def has_date(self, brain):
        return brain['silva-extramodificationtime'] is not None

    def dedup(self, item):
        url = item[0]
        if url in self.seen:
            return False
        self.seen.add(url)
        return True

    def process(self, brain):
        url = str(absoluteURL(brain, self.request))
        if self.trim_index and url.endswith('/index'):
            url = url[0:-6]
        return (url, brain['silva-extramodificationtime'].HTML4())

    def render(self):
        self.request.response.setHeader(
            'Content-Type', 'text/xml;charset=utf-8')
        return BufferedGeneratorStream(self.generate_xml())

    def generate_xml(self):
        yield ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for count, r in enumerate(self.pipe):
            if count > 50000:
                break
            yield """
<url>
   <loc>%s</loc>
   <lastmod>%s</lastmod>
</url>""" % (escape(r[0]), r[1])
        yield '\n</urlset>\n'
