from decimal import Decimal
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.models.row_field import PrepRows
from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefs
from o2lib.views.main import (
    totalize_data,
)
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import StopStepsException

from bordado.forms.listagem.pedido import PedidoForm
from bordado.models import Pedido
from bordado.views.base.filtro import FiltroParaView


__all__ = ['PedidoView']


class PedidoView(LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    CLIENTE = 'cliente__apelido'
    DATA = 'pedidoitem__data_pedido'
    BORDADO_NOME = 'pedidoitem__bordado__nome'
    BORDADO_CODIGO = 'pedidoitem__bordado__codigo'
    USUARIO = 'pedidoitem__usuario__username'
    QUANDO = 'pedidoitem__inserido_em'
    ENTREGA = 'entrega'
    QUANTIDADE = 'pedidoitem__quantidade'
    PRECO = 'pedidoitem__preco'
    PROGRAMACAO = 'pedidoitem__programacao'
    AJUSTE = 'pedidoitem__ajuste'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = PedidoForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/listagem/pedido.html'
        self.title_name = "Pedido - Listagem"
        self.get_args = ['numero']
        self.get_vars2form = True

        self.table_defs = TableDefs(
            {
                'numero': ['Nº', 'c'],
                self.DATA: ['Data', 'c'],
                self.CLIENTE: ['Cliente'],
                self.BORDADO_NOME: ['Bordado nome', 'c'],
                self.BORDADO_CODIGO: ['Código', 'c'],
                self.USUARIO: ["Usuário"],
                self.QUANDO: ["Quando"],
                self.ENTREGA: [],
                self.QUANTIDADE: ["Quantidade", 'r'],
                self.PRECO: ["Preço", 'r'],
                self.PROGRAMACAO: ["Programação", 'r'],
                self.AJUSTE: ["Ajuste", 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

        self.mount_steps = [
            self.init_query,
            self.filtra_cliente__apelido,
            (self.filtra_valor, ['numero']*2),
            (self.filtra_valor_de_ate, [self.DATA, 'data_de', 'data_ate']),
            (self.filtra_valor_de_ate, [
                self.ENTREGA, 'entrega_de', 'entrega_ate']),
            self.filtra_fechamento,
            self.order_query,
            self.exec_query,
            self.context_table,
        ]

    def init_query(self):
        self.query = Pedido.objects

    def filtra_fechamento(self):
        if self.fechamento == '-':
            self.context.update({
                'form_report_excludes': ['fechamento'],
            })
        elif self.fechamento == 'f':
            self.query = self.query.filter(entrega__isnull=False)
        elif self.fechamento == 'n':
            self.query = self.query.filter(entrega__isnull=True)

    def order_query(self):
        self.query = self.query.order_by(
            f'-{self.DATA}', '-numero'
        )

    def exec_query(self):
        self.data = self.query.values(
            *self.table_defs.all_fields)
        if self.data:
            self.data = queryset2dictlist(self.data)
        else:
            raise StopStepsException(
                "Filtro definido não seleciona nenhum pedido")

    def context_table(self):
        PrepRows(
            self.data,
        ).str_dash(
            (
                self.BORDADO_CODIGO,
                self.ENTREGA,
            )
        ).str(
            (
                self.BORDADO_NOME,
            ),
            '<Erro!>',
        ).process()

        self.context.update({
            'data': self.data,
        })
        self.table_defs.hfs_dict_context(self.context)
