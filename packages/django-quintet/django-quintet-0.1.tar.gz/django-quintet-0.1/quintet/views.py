# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView


class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        return kwargs

    def render(self, extra_context={}):
        context = self.get_context_data()
        context.update(extra_context)
        return self.render_to_response(context)

    def get(self, request):
        return self.render()
