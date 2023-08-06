from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView

from braces.views import LoginRequiredMixin

from ..models import Page
from ..edit.forms import PageForm


class PageListView(LoginRequiredMixin, ListView):
    template_name = 'dmcm/edit/page_list.html'
    model = Page


class PageCreateView(LoginRequiredMixin, CreateView):
    template_name = 'dmcm/edit/page_detail.html'
    model = Page
    form_class = PageForm

    def get_success_url(self):
        return reverse('dmcm:page_detail', args=(self.object.slug,))


class PageUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'dmcm/edit/page_detail.html'
    model = Page
    form_class = PageForm

    def get_success_url(self):
        return reverse('dmcm:page_detail', args=(self.object.slug,))
