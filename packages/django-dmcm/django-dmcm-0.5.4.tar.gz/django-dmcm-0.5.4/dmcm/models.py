"""Models used to store web pages."""

from django.db import models
from django.core.urlresolvers import reverse


class Page(models.Model):
    """Page information.

    :Fields:

        title : char
            Title of page.
        slug : slug
            Slugified version of Title.
        parent : foreign_key on page
            Parent page in site structure.
        published : date
            When page was published (usually on the blog).
        updated : date_time
            When page was last updated.
        content : text
            Page content in markdown format.
    """
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    parent = models.ForeignKey('self')
    published = models.DateField(null=True, blank=True)
    updated = models.DateTimeField(verbose_name='Time Updated', auto_now=True)
    content = models.TextField(verbose_name='Page body',
                               help_text='Use Markdown syntax.')

    def navigation_path(self):
        path = []
        parent = self.parent
        if parent != self:
            while parent != parent.parent:
                path.insert(0, {'title': parent.title,
                                'address': '/' + parent.slug + '/'})
                parent = parent.parent
            path.insert(0, {'title': parent.title, 'address':  reverse('dmcm:root')})
        return path

    def get_absolute_url(self):
        return reverse('dmcm:page_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title
