# -*- coding: utf-8 -*-
import json

from django.contrib import messages
from django.http import HttpResponse


class JsonResponseMixin(object):
    def render_json(self, data, status=200, encoder=None):
        kwargs = {
            'ensure_ascii': False
        }
        if encoder:
            kwargs['cls'] = encoder

        return HttpResponse(json.dumps(data, **kwargs),
            content_type='application/json; charset=UTF-8',
            status=status)


class GenericEditJsonResponseMixin(object):
    """Adds support for ajax response in Django's generic edit views.

    This should be used with "django.views.generic.edit" views.
    """
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json; charset=UTF-8'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(GenericEditJsonResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        return response

    def form_valid(self, form):
        response = super(GenericEditJsonResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            return self.render_to_json_response({
                'pk': self.object.pk,
            })
        return response


class JsonMessagesMixin(object):
    """Adds support for adding messages as json data."""
    def set_message(self, type, title, content):
        jsonMessage = json.dumps({'title': title, 'content': content})
        messages.add_message(self.request, type, jsonMessage)

    def set_json_info_message(self, title, content):
        self.set_message(messages.INFO, title, content)

    def set_json_success_message(self, title, content):
        self.set_message(messages.SUCCESS, title, content)

    def set_json_error_message(self, title, content):
        self.set_message(messages.ERROR, title, content)
