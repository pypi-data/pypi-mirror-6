#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from ujson import loads
from tornado.gen import coroutine
from tornado.httpclient import HTTPError

from holmes.handlers import BaseHandler


class UserLoginHandler(BaseHandler):

    @coroutine
    def get(self, access_token):
        api_url = 'https://www.googleapis.com/oauth2/v1/tokeninfo'
        url = '%s?access_token=%s' % (api_url, access_token)

        try:
            result = yield self.application.http_client.fetch(
                url,
                proxy_host=self.application.config.HTTP_PROXY_HOST,
                proxy_port=self.application.config.HTTP_PROXY_PORT
            )
        except HTTPError:
            err = sys.exc_info()[1]
            data = loads(err.response.body)
            error = data.get('error', None)
            if error:
                self.write_json(error)
            self.write_json('Error')
            return

        data = loads(result.body)

        #import pdb; pdb.set_trace()

        # Verify that the access token is valid for this app.
        if data.get('issued_to') != self.application.config.GOOGLE_CLIENT_ID:
            msg = "Token's client ID does not match app's."
            self.set_status(401)
            self.write_json(msg)
            return

        user_id = data.get('user_id')
        user_email = data.get('email')

        self.write_json('Successfully connected user.')
