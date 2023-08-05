#!/usr/bin/python
# -*- coding: utf-8 -*-

from holmes.facters import Facter


class HeadingHierarchyFacter(Facter):
    @classmethod
    def get_fact_definitions(cls):
        return {
            'total.heading.h1': {
                'title': 'H1 count',
                'description': lambda value: "This page has %d H1 tags." % value
            },
            'total.heading.h2': {
                'title': 'H2 count',
                'description': lambda value: "This page has %d H2 tags." % value
            },
            'total.heading.h3': {
                'title': 'H3 count',
                'description': lambda value: "This page has %d H3 tags." % value
            },
            'total.heading.h4': {
                'title': 'H4 count',
                'description': lambda value: "This page has %d H4 tags." % value
            },
            'total.heading.h5': {
                'title': 'H5 count',
                'description': lambda value: "This page has %d H5 tags." % value
            },
            'total.heading.h6': {
                'title': 'H6 count',
                'description': lambda value: "This page has %d H6 tags." % value
            }
        }

    def get_facts(self):
        heading = self.get_heading()

        for i in xrange(1, 7):
            tag = 'h%d' % i
            self.add_fact(
                key='total.heading.%s' % tag,
                value=len(heading[tag])
            )

    def get_heading(self):
        heading = []

        for i in xrange(1, 7):
            tag = 'h%d' % i
            heading.append({tag: self.reviewer.current_html.cssselect(tag)})

        return heading
