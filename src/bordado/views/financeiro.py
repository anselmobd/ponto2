from pprint import pprint

from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from django.views import View

# from utils.views import totalize_data

# import cd.queries as queries
# import cd.forms


class Financeiro(View):

    def __init__(self):
        # self.Form_class = cd.forms.HistoricoForm
        self.template_name = 'bordado/financeiro.html'
        self.title_name = 'Financeiro'

    # def mount_context(self, cursor, op):
    #     context = {
    #         'op': op,
    #     }

    #     return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        # form = self.Form_class()
        # context['form'] = form
        return render(request, self.template_name, context)

    # def post(self, request, *args, **kwargs):
    #     context = {'titulo': self.title_name}
    #     form = self.Form_class(request.POST)
    #     form.data = form.data.copy()
    #     if 'op' in kwargs and kwargs['op'] is not None:
    #         form.data['op'] = kwargs['op']
    #     if form.is_valid():
    #         op = form.cleaned_data['op']
    #         cursor = connection.cursor()
    #         context.update(self.mount_context(cursor, op))
    #     context['form'] = form
    #     return render(request, self.template_name, context)
