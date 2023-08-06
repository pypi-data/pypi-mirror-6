from __future__ import absolute_import

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

import markdown

EXTENSIONS = ['extra', 'tables', 'toc']

def markdown_to_html(value):
    """
    Runs Markdown over a given value, using various
    extensions python-markdown supports.
    """
    return mark_safe(markdown.markdown(force_text(value),
                                       EXTENSIONS,
                                       safe_mode=False))

