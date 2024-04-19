from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.urls import reverse

from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefs

from bordado.forms import FinanceiroForm
from bordado.models import (
    Cobranca,
    Lancamento,
    Pedido,
)


class Financeiro(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super().__init__()
        self.Form_class = FinanceiroForm
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/financeiro.html'
        self.title_name = 'Financeiro'
        self.table_defs = TableDefs(
            {
                'data parcela': [],
                'n_parcelas': ['Nº de parcelas'],
                'informacao': ['Informação'],
                'valor': [None, 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def mount_context(self):
        lancamento = Lancamento.objects
        if self.pedido_numero:
            try:
                pedido = Pedido.objects.get(numero=self.pedido_numero)
                lancamento = lancamento.filter(pedido=pedido)  # erro!
            except Pedido.DoesNotExist:
                ...
        if self.cobranca_id:
            try:
                cobranca = Cobranca.objects.get(id=self.cobranca_id)
                lancamento = lancamento.filter(cobranca=cobranca)  # erro!
            except Cobranca.DoesNotExist:
                ...
        data = queryset2dictlist(lancamento)
        self.context.update({
            'data': data,
        })
        self.table_defs.hfs_dict_context(self.context)
