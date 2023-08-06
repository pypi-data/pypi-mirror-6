# -*- coding: utf-8 -*-
from django.views.generic import TemplateView


class NotCMSTestView(TemplateView):
    """
    A simple view used for testing purpose
    """
    template_name = '_layouts/base.html'


class RootTestView(TemplateView):
    """
    A root view for testing purpose
    """
    template_name = '_layouts/base.html'
