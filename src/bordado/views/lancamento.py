from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.urls import reverse

from o2lib.models.dictlist import queryset2dictlist
from o2lib.models.row_field import PrepRows
from o2lib.table_defs import TableDefs
from o2lib.views.base.get_post import O2BaseGetPostView

from bordado.forms import FinanceiroForm
from bordado.models import (
    Cobranca,
    Lancamento,
    Pedido,
)


class LancamentoView(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self):
        super().__init__()
        self.Form_class = FinanceiroForm
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/lancamento.html'
        self.title_name = 'Lançamento'
        self.table_defs = TableDefs(
            {
                'cobranca__pedidoitemcobranca__pedido_item__pedido': ['Pedido', 'c'],
                'data': [],
                'informacao': ['Informação', 'c'],
                'cobranca__comunicacao__descricao': ['Comunicação', 'c'],
                'cobranca__nf': ['NF', 'c'],
                'cobranca': ['Cobrança', 'c'],
                'parcela': [None, 'c'],
                'n_parcelas': ['Nºparcelas', 'c'],
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
                lancamento = lancamento.filter(
                    cobranca__pedidoitemcobranca__pedido_item__pedido=pedido)
            except Pedido.DoesNotExist:
                ...
        if self.cobranca_id:
            try:
                cobranca = Cobranca.objects.get(id=self.cobranca_id)
                lancamento = lancamento.filter(cobranca=cobranca)
            except Cobranca.DoesNotExist:
                ...

        data = queryset2dictlist(lancamento)
        pprint(data)

        data = lancamento.values(*self.table_defs.all_fields)
        
        PrepRows(
            data,
        ).str_dash(
            (
                'informacao',
                'cobranca__comunicacao__descricao',
                'cobranca__nf',
                'cobranca',
            )
        ).process()

        self.context.update({
            'data': data,
        })
        self.table_defs.hfs_dict_context(self.context)
