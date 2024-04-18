from pprint import pprint

from django.db import connection
from django.shortcuts import render
from django.urls import reverse

from o2lib.views.base.get_post import O2BaseGetPostView

from bordado.forms import FinanceiroForm


class Financeiro(O2BaseGetPostView):

    def __init__(self):
        super().__init__()
        self.Form_class = FinanceiroForm
        self.cleaned_data2self = True
        self.template_name = 'bordado/financeiro.html'
        self.title_name = 'Financeiro'

    def mount_context(self):
        self.context.update({
            'pedido': self.pedido,
        })
