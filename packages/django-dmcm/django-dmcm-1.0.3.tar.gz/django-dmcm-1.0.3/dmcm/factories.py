"""Factories used to create data for testing."""
from __future__ import absolute_import

from .models import Page

import factory

class PageFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Page

    title = factory.Sequence(lambda n: 'Test Page {0}'.format(n))
    slug = title
    content = '# %s content' % title