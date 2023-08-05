
from __future__ import absolute_import

import flask

from instantauth import Authentication

flask.Request.want_form_data_parsed = False

class FlaskAuthentication(Authentication):
    def from_request(self):
        raw_data = flask.request.data
        data = self.session_handler.decode_data(raw_data)
        context = self.get_context(data)
        flask.request.form = context.data
        flask.request.session = context.session
        return context

    def from_first_request(self, type=None, **params):
        raw_data = flask.request.data
        data = self.session_handler.decode_data(raw_data)
        context = self.get_first_context(data, type, **params)
        flask.request.form = context.data
        flask.request.session = context.session
        return context
