from simplevhost.shortcuts import get_template_name
from django.views.generic.detail import DetailView


class SimpleVhostDetailView(DetailView):
    def get_template_names(self):
        template_names = super(SimpleVhostDetailView, self).get_template_names()
        return [get_template_name(self.request, x) for x in template_names] + template_names
