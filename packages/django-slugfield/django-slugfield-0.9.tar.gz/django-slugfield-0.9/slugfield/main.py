# coding=utf8

import re

from django import forms
from django.db import models
from django.forms.widgets import TextInput
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify as django_slugify


class SlugFormField(forms.CharField):
    widget = TextInput
    default_error_message = _("Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.")

    def __init__(self, slugify=django_slugify, populate_from=None, widget=None, **kwargs):

        self.slugify = slugify
        widget = widget or self.widget

        # widget can be class or object, e.g., TextInput or TextInput({'class': 'big'})
        # that's why we use decorator instead of inheritance
        if isinstance(widget, type):
            widget = widget()

        def add_populating(bound_value_from_datadict):
            def value_from_datadict(data, files, name):
                value = bound_value_from_datadict(data, files, name)
                if not value and populate_from:
                    # change data key from 'option_prefix_<slug>' to 'option_prefix_<populate_from>'
                    html_name_re = re.compile('({})$'.format(re.escape(name)))
                    name = html_name_re.sub(populate_from, name)
                    value = data.get(name, '')
                    value = self.slugify(value)
                    if value:
                        value += '?'
                return value
            return value_from_datadict

        widget.value_from_datadict = add_populating(widget.value_from_datadict)
        kwargs['widget'] = widget

        super(SlugFormField, self).__init__(**kwargs)

    def validate(self, value):
        if self.slugify(value) != value:
            raise ValidationError(self.default_error_message, code='invalid')
        super(SlugFormField, self).validate(value)


class SlugField(models.CharField):
    description = 'Slug (up to %(max_length)s)'

    def __init__(self, *args, **kwargs):

        self.populate_from = kwargs.pop('populate_from', None)
        self.slugify = kwargs.pop('slugify', django_slugify)
        self.empty_values = (None,)

        self.invalid_slug_message = kwargs.pop('mes', 'invalid slug mes')

        kwargs.setdefault('unique', True)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('max_length', 200)

        super(SlugField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'slugify': self.slugify,
            'populate_from': self.populate_from,
            'form_class': SlugFormField,
        }
        defaults.update(kwargs)
        return super(SlugField, self).formfield(**defaults)
