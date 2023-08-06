#!/usr/bin/python
# -*- coding: utf-8 -*-

from holmes.validators.base import Validator


class HeadingHierarchyValidator(Validator):

    @classmethod
    def get_violation_description(cls, value):
        return (
            'Heading hierarchy values bigger than %s characters aren`t good '
            'for Search Engines. This elements were found:'
            '<ul class="violation-hh-list">%s</ul>' % (
                value['max_size'],
                ''.join([
                    '<li><span class="hh-type">%s</span>: %s</li>' % (key, desc)
                    for key, desc in value['hh_list']
                ])
            )
        )

    @classmethod
    def get_violation_definitions(cls):
        return {
            'page.heading_hierarchy.size': {
                'title': 'Maximum size of a heading hierarchy',
                'description': cls.get_violation_description,
                'category': 'SEO'
            }
        }

    def validate(self):
        hh_list = self.review.data.get('page.heading_hierarchy', [])

        violations = []
        for key, desc in hh_list:
            if len(desc) > self.config.MAX_HEADING_HIEARARCHY_SIZE:
                violations.append((key, desc))

        if violations:
            self.add_violation(
                key='page.heading_hierarchy.size',
                value={
                    'max_size': self.config.MAX_HEADING_HIEARARCHY_SIZE,
                    'hh_list': violations
                },
                points=20 * len(violations)
            )
