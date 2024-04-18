from pprint import pprint

from django.db import connection
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from bordado.forms import FinanceiroForm


class Financeiro(View):

    def __init__(self):
        self.Form_class = FinanceiroForm
        self.template_name = 'bordado/financeiro.html'
        self.context = {'titulo': 'Financeiro'}

    def mount_context(self, form):
        self.context.update({
            'pedido': form.data['pedido'],
        })

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.Form_class(request.POST)
        pprint(form.fields['pedido'].__dict__)
        pprint(form.data['pedido'])
        self.context['form'] = form
        if form.is_valid():
            self.mount_context(form)
        return render(request, self.template_name, self.context)
