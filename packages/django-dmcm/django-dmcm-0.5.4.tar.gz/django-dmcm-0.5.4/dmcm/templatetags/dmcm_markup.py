"""
Markdown template filter.

Requires the Python-markdown library from
      http://www.freewisdom.org/projects/python-markdown
"""
from __future__ import absolute_import

from django import template
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from ..utils import markdown_to_html

register = template.Library()


@register.filter(is_safe=True)
def markdown(value, arg=''):
    """
    Runs Markdown over a given value.
    Syntax:: {{ value|markdown }}
    """
    return markdown_to_html(value)

