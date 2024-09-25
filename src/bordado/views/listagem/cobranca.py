from decimal import Decimal
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.form.form_report import form_report
from o2lib.models.row_field import PrepRows
from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefsHpS
from o2lib.views.group import group_rowspan
from o2lib.views.totalize import totalize_grouped_data
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import StopStepsException

from bordado.forms.listagem.cobranca import ListagemCobrancaForm
from bordado.models import Cobranca
from bordado.views.base.filtro import FiltroParaView


__all__ = ['ListagemCobrancaView']


class ListagemCobrancaView(
        LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    CLIENTE = 'cliente__apelido'
    COMUNICACAO = 'comunicacao__descricao'
    PEDIDO = 'pedidoitemcobranca__pedido_item__pedido'
    QUANTIDADE = 'pedidoitemcobranca__pedido_item__quantidade'
    BORDADO_NOME = 'pedidoitemcobranca__pedido_item__bordado__nome'
    BORDADO_CODIGO = 'pedidoitemcobranca__pedido_item__bordado__codigo'
    OBSERVACAO = 'pedidoitemcobranca__pedido_item__observacao'
    VALOR = 'pedidoitemcobranca__valor'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = ListagemCobrancaForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/listagem/cobranca.html'
        self.title_name = "Cobrança - Listagem"
        self.get_args = ['numero']
        self.get_vars2form = True

        self.table_defs = TableDefsHpS({
            self.CLIENTE: ['Cliente'],
            'id': ['Nº', 'c'],
            'informacao': ['Informação'],
            self.COMUNICACAO: ['Tipo'],
            'nf': ['NF', 'c'],
            'data': ['Data', 'c'],
            'parcelamento': ['Parcelamento', 'c'],
            self.PEDIDO: ['Pedido', 'c'],
            self.QUANTIDADE: ['Quantidade', 'r'],
            self.BORDADO_NOME: ['Bordado nome', 'c'],
            self.BORDADO_CODIGO: ['Código', 'c'],
            self.OBSERVACAO: ['Obs.', 'c'],
            self.VALOR: ['Valor pedido', 'r'],
            'usuario__username': ["Usuário"],
            'quando': [],
        })

        self.mount_steps = [
            self.init_query,
            self.filtra_cliente__apelido,
            (self.filtra_valor, ['id', 'numero']),
            (self.filtra_valor_de_ate, ['data', 'data_de', 'data_ate']),
            self.order_query,
            self.exec_query,
            self.context_table,
            self.form_report,
        ]

    def init_query(self):
        self.query = Cobranca.objects

    def order_query(self):
        self.query = self.query.order_by(
            self.CLIENTE, '-data', '-id'
        )

    def exec_query(self):
        self.data = self.query.values(
            *self.table_defs.all_fields)
        if self.data:
            self.data = queryset2dictlist(self.data)
        else:
            raise StopStepsException(
                "Filtro definido não seleciona nenhuma cobrança")

    def context_table(self):
        PrepRows(
            self.data,
        ).str_dash(
            (
                'nf',
                'informacao',
                'parcelamento',
                self.BORDADO_CODIGO,
                self.OBSERVACAO,
            )
        ).str(
            (
                self.PEDIDO,
                self.QUANTIDADE,
                self.BORDADO_NOME,
            ),
            '<Erro!>',
        ).none(
            self.VALOR, Decimal('0.00')
        ).process()

        group = [
            self.CLIENTE,
            'id',
            'informacao',
            self.COMUNICACAO,
            'nf',
            'data',
            'parcelamento',
        ]

        group_rowspan(self.data, group)
        totalize_grouped_data(
            self.data,
            {
                'group': group,
                'sum': [self.VALOR],
                'descr': {self.PEDIDO: 'Valor itens:'},
                'global_sum': [self.VALOR],
                'global_descr': {'nf': 'Total:'},
                # 'global_row_if': 'rowspan',
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
            }
        )

        self.context.update({
            'data': self.data,
            'group': group,
        })
        self.table_defs.hfs_dict_context(self.context)

    def form_report(self):
        self.context.update({
            'form_report': form_report(self.form),
        })
