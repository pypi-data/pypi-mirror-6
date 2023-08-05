#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import re
import lxml.etree

from holmes.facters import Facter


ROBOTS_SITEMAP = re.compile('Sitemap:\s+(.*)')


class SitemapFacter(Facter):

    def get_facts(self):
        self.async_get(self.rebase('/robots.txt'), self.handle_robots_loaded)

        self.review.data['sitemap.data'] = {}
        self.review.data['sitemap.urls'] = {}
        self.review.data['sitemap.files'] = set()
        self.review.data['sitemap.files.size'] = {}
        self.review.data['sitemap.files.urls'] = {}
        self.review.data['total.size.sitemap'] = 0
        self.review.data['total.size.sitemap.gzipped'] = 0

        self.add_fact(
            key='total.sitemap.indexes',
            value=0,
            unit='',
            title='Total Sitemap indexes'
        )

        self.add_fact(
            key='total.sitemap.urls',
            value=0,
            unit='',
            title='Total Sitemap urls'
        )

        self.add_fact(
            key='total.size.sitemap',
            value=0,
            unit='kb',
            title='Total Sitemap size'
        )

        self.add_fact(
            key='total.size.sitemap.gzipped',
            value=0,
            unit='kb',
            title='Total Sitemap size gzipped'
        )

    def get_sitemaps(self, response):
        sitemaps = [self.rebase('/sitemap.xml')]

        if response.status_code > 399:
            return sitemaps

        return sitemaps + ROBOTS_SITEMAP.findall(response.text)

    def handle_sitemap_loaded(self, url, response):
        logging.debug('Got sitemap %s with status %s' % (url, response.status_code))
        self.review.data['sitemap.data'][url] = response

        namespaces = [
            ('sm', 'http://www.sitemaps.org/schemas/sitemap/0.9'),
        ]

        if response.status_code > 399 or response.text is None or not response.text.strip():
            return

        self.review.facts['total.sitemap.indexes']['value'] += 1

        size_sitemap = len(response.text) / 1024.0
        size_gzip = len(self.to_gzip(response.text)) / 1024.0

        self.review.data['sitemap.files.urls'][url] = 0
        self.review.data['sitemap.files.size'][url] = size_sitemap
        self.review.data['sitemap.urls'][url] = set()

        self.review.facts['total.size.sitemap']['value'] += size_sitemap
        self.review.data['total.size.sitemap'] += size_sitemap

        self.review.facts['total.size.sitemap.gzipped']['value'] += size_gzip
        self.review.data['total.size.sitemap.gzipped'] += size_gzip

        tree = lxml.etree.fromstring(response.text)

        for sitemap in tree.xpath('//sm:sitemap | //sitemap', namespaces=namespaces):
            for loc in sitemap.xpath('sm:loc | loc', namespaces=namespaces):
                loc = loc.text.strip()
                self.review.data['sitemap.files'].add(loc)
                self.review.data['sitemap.files.urls'][url] += 1
                self.async_get(loc, self.handle_sitemap_loaded)

        for sitemap in tree.xpath('//sm:url | //url', namespaces=namespaces):
            for loc in sitemap.xpath('sm:loc | loc', namespaces=namespaces):
                loc = loc.text.strip()
                self.review.data['sitemap.urls'][url].add(loc)
                self.review.data['sitemap.files.urls'][url] += 1
                self.review.facts['total.sitemap.urls']['value'] += 1
                self.reviewer.enqueue(loc)

    def handle_robots_loaded(self, url, response):
        sitemaps = self.get_sitemaps(response)

        for sitemap in sitemaps:
            self.async_get(sitemap, self.handle_sitemap_loaded)
