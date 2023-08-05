#!/usr/bin/python
# -*- coding: utf-8 -*-

from derpconf.config import Config  # NOQA


Config.define('WORKER_SLEEP_TIME', 10, 'Main loop sleep time', 'Worker')
Config.define('ZOMBIE_WORKER_TIME', 200,
              'Time to remove a Worker from API List (must be greater than WORKER_SLEEP_TIME + Validation time)', 'API')

Config.define('CONNECT_TIMEOUT_IN_SECONDS', 20, 'Number of seconds a connection can take.', 'Worker')
Config.define('REQUEST_TIMEOUT_IN_SECONDS', 60, 'Number of seconds a request can take.', 'Worker')

Config.define('HOLMES_API_URL', 'http://localhost:2368', 'URL that Worker will communicate with API', 'Worker')

Config.define('LOG_LEVEL', 'ERROR', 'Default log level', 'Logging')
Config.define('LOG_FORMAT', '%(asctime)s:%(levelname)s %(module)s - %(message)s',
              'Log Format to be used when writing log messages', 'Logging')
Config.define('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S',
              'Date Format to be used when writing log messages.', 'Logging')

Config.define('FACTERS', [], 'List of classes to get facts about a website', 'Review')
Config.define('VALIDATORS', [], 'List of classes to validate a website', 'Review')
Config.define('REVIEW_EXPIRATION_IN_SECONDS', 6 * 60 * 60, 'Number of seconds that a review expires in.', 'Review')

Config.define('MAX_ENQUEUE_BUFFER_LENGTH', 1000,
              'Number of urls to enqueue before submitting to the /pages route', 'Validators')

Config.define('MAX_IMG_REQUESTS_PER_PAGE', 50,
              'Maximum number of images per page', 'Image Request Validator')
Config.define('MAX_KB_SINGLE_IMAGE', 100,
              'Maximum size of a single image', 'Image Request Validator')
Config.define('MAX_IMG_KB_PER_PAGE', 1000,
              'Maximum size of images per page', 'Image Request Validator')

Config.define('MAX_CSS_REQUESTS_PER_PAGE', 5,
              'Maximum number of external stylesheets per page', 'CSS Request Validator')
Config.define('MAX_CSS_KB_PER_PAGE_AFTER_GZIP', 50,
              'Maximum size of stylesheets per page after gzip', 'CSS Request Validator')

Config.define('MAX_JS_REQUESTS_PER_PAGE', 5,
              'Maximum number of external scripts per page', 'JS Request Validator')
Config.define('MAX_JS_KB_PER_PAGE_AFTER_GZIP', 50,
              'Maximum size of scripts per page after gzip', 'JS Request Validator')

Config.define('MAX_TITLE_SIZE', 80,
              'Title tags longer than 80 characters may be truncated in the results', 'Title Validator')

Config.define('ORIGIN', '*', 'Access Control Allow Origin header value', 'Web')

Config.define('HTTP_PROXY_HOST', None, 'HTTP Proxy Host to use', 'Web')
Config.define('HTTP_PROXY_PORT', None, 'HTTP Proxy Port to use', 'Web')

Config.define('COMMIT_ON_REQUEST_END', True, 'Commit on request end', 'DB')

Config.define('REDISHOST', 'localhost', 'Redis host', 'Redis')
Config.define('REDISPORT', 7575, 'Redis port', 'Redis')
Config.define('REDISPASS', None, 'Redis password in case of auth', 'Redis')

Config.define('REQUIRED_META_TAGS', [], 'List of required meta tags', 'Meta tag Validator')
