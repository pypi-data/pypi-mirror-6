#!/usr/bin/env python
# encoding: utf-8
"""
widgets.py

Created by Luan Fonseca on 2013-01-21.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django import forms
from django.utils.safestring import mark_safe
from django.template.defaultfilters import floatformat

from hstore_flattenfields.utils import str2literal


class SelectMultipleWidget(forms.SelectMultiple):
    def render(self, name, value='', attrs={}, choices=()):
        html = super(SelectMultipleWidget, self).render(
            name, str2literal(value), attrs, choices)
        return mark_safe(html)
