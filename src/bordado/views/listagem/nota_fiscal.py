from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.form.form_report import form_report
from o2lib.models.row_field import PrepRows
from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefsHpS
from o2lib.views.main import (
    group_rowspan,
    totalize_grouped_data,
)
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import StopStepsException

from bordado.forms.listagem.nota_fiscal import ListagemNotaFiscalForm
from bordado.models import Cobranca
from bordado.views.base.filtro import FiltroParaView


__all__ = ['ListagemNotaFiscalView']


class ListagemNotaFiscalView(
        LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    CLIENTE = 'cliente__apelido'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = ListagemNotaFiscalForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/listagem/nota_fiscal.html'
        self.title_name = 'Nota fiscal - Listagem'
        self.get_args = ['nf']

        self.table_defs = TableDefsHpS({
            self.CLIENTE: ['Cliente'],
            'nf': ['NF', 'c'],
            'id': ['Cobrança', 'c'],
            'data': ['Data', 'c'],
            'valor': ['Valor cobrança', 'r'],
        })

        self.mount_steps = [
            self.init_query,
            self.filtra_cliente__apelido,
            (self.filtra_valor, ['nf']*2),
            (self.filtra_valor_de_ate, ['data', 'data_de', 'data_ate']),
            self.com_faturamento,
            self.order_query,
            self.exec_query,
            self.prep_table,
            self.totalize_table,
            self.context_table,
            self.form_report,
        ]

    def init_query(self):
        self.query = Cobranca.objects

    def order_query(self):
        self.query = self.query.order_by(
            self.CLIENTE, '-nf', '-data', '-id'
        )

    def com_faturamento(self):
        self.query = self.query.exclude(nf=0).exclude(nf__isnull=True)

    def exec_query(self):
        self.data = self.query.values(
            *self.table_defs.all_fields)
        if self.data:
            self.data = queryset2dictlist(self.data)
        else:
            raise StopStepsException(
                "Filtro definido não seleciona nenhum faturamento")

    def prep_table(self):
        PrepRows(
            self.data,
        ).str_dash(
            (
                'nf',
            )
        ).process()

    def totalize_table(self):
        self.group = [
            'nf',
            self.CLIENTE,
        ]
        group_rowspan(self.data, self.group)
        totalize_grouped_data(
            self.data,
            {
                'group': self.group,
                'sum': ['valor'],
                'descr': {self.CLIENTE: "Valor NF:"},
                'global_sum': ['valor'],
                'global_descr': {self.CLIENTE: "Total:"},
                'row_if': 'rowspan',
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
            }
        )

    def context_table(self):
        self.context.update({
            'data': self.data,
            'group': self.group,
        })
        self.table_defs.hfs_dict_context(self.context)

    def form_report(self):
        self.context.update({
            'form_report': form_report(self.form),
        })
