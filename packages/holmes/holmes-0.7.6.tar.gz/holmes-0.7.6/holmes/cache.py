#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.concurrent import return_future
from ujson import loads, dumps
from octopus.model import Response

from holmes.models import Domain, Page


class Cache(object):
    def __init__(self, application):
        self.application = application
        self.redis = self.application.redis
        self.db = self.application.db
        self.config = self.application.config

    def get_domain_name(self, domain_name):
        if isinstance(domain_name, Domain):
            return domain_name.name

        return domain_name or 'page'

    @return_future
    def has_key(self, key, callback):
        self.redis.exists(key, callback)

    @return_future
    def increment_violations_count(self, domain_name, increment=1, callback=None):
        self.increment_count(
            'violation-count',
            domain_name,
            lambda domain: domain.get_violation_data(self.db),
            increment,
            callback
        )

    @return_future
    def increment_active_review_count(self, domain_name, increment=1, callback=None):
        self.increment_count(
            'active-review-count',
            domain_name,
            lambda domain: domain.get_active_review_count(self.db),
            increment,
            callback
        )

    @return_future
    def increment_page_count(self, domain_name=None, increment=1, callback=None):
        self.increment_count(
            'page-count',
            domain_name,
            lambda domain: domain.get_page_count(self.db),
            increment,
            callback
        )

    def increment_count(self, key, domain_name, get_default_method, increment=1, callback=None):
        key = '%s-%s' % (self.get_domain_name(domain_name), key)
        self.has_key(key, self.handle_has_key(key, domain_name, get_default_method, increment, callback))

    def handle_has_key(self, key, domain_name, get_default_method, increment, callback):
        def handle(has_key):
            domain = domain_name
            if domain and not isinstance(domain, Domain):
                domain = Domain.get_domain_by_name(domain_name, self.db)

            #if not domain:
                #callback(None)
                #return

            if has_key:
                self.redis.incrby(key, increment, callback=callback)
            else:
                if domain is None:
                    value = Page.get_page_count(self.db) + increment - 1
                else:
                    value = get_default_method(domain) + increment - 1

                self.redis.set(key, value, callback=callback)

        return handle

    @return_future
    def get_page_count(self, domain_name=None, callback=None):
        self.get_count(
            'page-count',
            domain_name,
            int(self.config.PAGE_COUNT_EXPIRATION_IN_SECONDS),
            lambda domain: domain.get_page_count(self.db),
            callback=callback
        )

    @return_future
    def get_violation_count(self, domain_name, callback=None):
        self.get_count(
            'violation-count',
            domain_name,
            int(self.config.PAGE_COUNT_EXPIRATION_IN_SECONDS),
            lambda domain: domain.get_violation_data(self.db),
            callback=callback
        )

    @return_future
    def get_active_review_count(self, domain_name, callback=None):
        self.get_count(
            'active-review-count',
            domain_name,
            int(self.config.ACTIVE_REVIEW_COUNT_EXPIRATION_IN_SECONDS),
            lambda domain: domain.get_active_review_count(self.db),
            callback=callback
        )

    def get_count(self, key, domain_name, expiration, get_count_method, callback=None):
        cache_key = '%s-%s' % (self.get_domain_name(domain_name), key)
        self.redis.get(cache_key, callback=self.handle_get_count(key, domain_name, expiration, get_count_method, callback))

    def handle_get_count(self, key, domain_name, expiration, get_count_method, callback):
        def handle(count):
            if count is not None:
                callback(int(count))
                return

            domain = domain_name
            if domain and not isinstance(domain, Domain):
                domain = Domain.get_domain_by_name(domain_name, self.db)

            if domain is None:
                count = Page.get_page_count(self.db)
            else:
                count = get_count_method(domain)

            cache_key = '%s-%s' % (self.get_domain_name(domain), key)

            self.redis.setex(
                key=cache_key,
                value=int(count),
                seconds=expiration,
                callback=self.handle_set_count(count, callback)
            )

        return handle

    def handle_set_count(self, count, callback):
        def handle(*args, **kw):
            callback(count)

        return handle

    @return_future
    def lock_page(self, url, callback=None):
        expiration = self.config.URL_LOCK_EXPIRATION_IN_SECONDS

        self.redis.setex(
            key='%s-lock' % url,
            value=1,
            seconds=expiration,
            callback=callback
        )

    @return_future
    def has_lock(self, url, callback=None):
        self.redis.get(
            key='%s-lock' % url,
            callback=self.handle_get_lock_page(url, callback)
        )

    def handle_get_lock_page(self, url, callback):
        def handle(value):
            callback(value == '1')

        return handle

    @return_future
    def release_lock_page(self, url, callback):
        self.redis.delete('%s-lock' % url, callback=callback)

    @return_future
    def lock_next_job(self, url, callback=None):
        expiration = self.config.NEXT_JOB_URL_LOCK_EXPIRATION_IN_SECONDS

        self.redis.setex(
            key='%s-next-job-lock' % url,
            value=1,
            seconds=expiration,
            callback=callback
        )

    @return_future
    def has_next_job_lock(self, url, callback=None):
        self.redis.get(
            key='%s-next-job-lock' % url,
            callback=self.handle_get_next_job_lock(url, callback)
        )

    def handle_get_next_job_lock(self, url, callback):
        def handle(value):
            callback(value == '1')

        return handle


class SyncCache(object):
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis

    def has_key(self, key):
        return self.redis.exists(key)

    def get_domain_name(self, domain_name):
        if isinstance(domain_name, Domain):
            return domain_name.name

        return domain_name or 'page'

    def increment_violations_count(self, domain_name, increment=1):
        self.increment_count(
            'violation-count',
            domain_name,
            lambda domain: domain.get_violation_data(self.db),
            increment
        )

    def increment_active_review_count(self, domain_name, increment=1):
        self.increment_count(
            'active-review-count',
            domain_name,
            lambda domain: domain.get_active_review_count(self.db),
            increment,
        )

    def increment_page_count(self, domain_name=None, increment=1):
        self.increment_count(
            'page-count',
            domain_name,
            lambda domain: domain.get_page_count(self.db),
            increment,
        )

    def increment_count(self, key, domain_name, get_default_method, increment=1):
        key = '%s-%s' % (self.get_domain_name(domain_name), key)

        has_key = self.has_key(key)

        domain = domain_name
        if domain and not isinstance(domain, Domain):
            domain = Domain.get_domain_by_name(domain_name, self.db)

        if has_key:
            self.redis.incrby(key, increment)
        else:
            if domain is None:
                value = Page.get_page_count(self.db) + increment - 1
            else:
                value = get_default_method(domain) + increment - 1

            self.redis.set(key, value)

    def get_page_count(self, domain_name=None):
        self.get_count(
            'page-count',
            domain_name,
            int(self.config.PAGE_COUNT_EXPIRATION_IN_SECONDS),
            lambda domain: domain.get_page_count(self.db),
        )

    def get_violation_count(self, domain_name):
        self.get_count(
            'violation-count',
            domain_name,
            int(self.config.PAGE_COUNT_EXPIRATION_IN_SECONDS),
            lambda domain: domain.get_violation_data(self.db),
        )

    def get_active_review_count(self, domain_name):
        self.get_count(
            'active-review-count',
            domain_name,
            int(self.config.ACTIVE_REVIEW_COUNT_EXPIRATION_IN_SECONDS),
            lambda domain: domain.get_active_review_count(self.db)
        )

    def get_count(self, key, domain_name, expiration, get_count_method):
        cache_key = '%s-%s' % (self.get_domain_name(domain_name), key)

        count = self.redis.get(cache_key)

        if count is not None:
            return int(count)

        domain = domain_name
        if domain and not isinstance(domain, Domain):
            domain = Domain.get_domain_by_name(domain_name, self.db)

        if domain is None:
            count = Page.get_page_count(self.db)
        else:
            count = get_count_method(domain)

        cache_key = '%s-%s' % (self.get_domain_name(domain), key)

        self.redis.setex(
            key=cache_key,
            value=int(count),
            seconds=expiration,
        )

        return int(count)

    def get_request(self, url):
        cache_key = "urls-%s" % url

        contents = self.redis.get(cache_key)

        if not contents:
            return url, None

        body = self.redis.get('%s-body' % cache_key)

        item = loads(contents)
        response = Response(
            url=url,
            status_code=item['status_code'],
            headers=item['headers'],
            cookies=item['cookies'],
            text=body,
            effective_url=item['effective_url'],
            error=item['error'],
            request_time=float(item['request_time'])
        )

        response.from_cache = True

        return url, response

    def set_request(self, url, status_code, headers, cookies, text, effective_url, error, request_time, expiration):
        cache_key = "urls-%s" % url
        body_key = '%s-body' % cache_key

        try:
            self.redis.setex(
                cache_key,
                expiration,
                dumps({
                    'url': url,
                    'status_code': status_code,
                    'headers': headers,
                    'cookies': cookies,
                    'effective_url': effective_url,
                    'error': error,
                    'request_time': str(request_time)
                }),
            )

            self.redis.setex(
                body_key,
                expiration,
                text
            )
        except Exception, err:
            import pdb; pdb.set_trace()
