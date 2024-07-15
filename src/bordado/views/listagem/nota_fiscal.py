from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.models.row_field import PrepRows
from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefs
from o2lib.views.main import (
    group_rowspan,
    totalize_grouped_data,
)
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import (
    StepErrorException,
    StopStepsException, 
)

from bordado.forms.listagem.nota_fiscal import NotaFiscalForm
from bordado.models import (
    Cliente,
    Cobranca,
)
from bordado.views.base.filtro import FiltroParaView


__all__ = ['NotaFiscalView']


class NotaFiscalView(LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    CLIENTE = 'cliente__apelido'

    def __init__(self, *args, **kwargs):
        super(NotaFiscalView, self).__init__(*args, **kwargs)
        self.Form_class = NotaFiscalForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/listagem/nota_fiscal.html'
        self.title_name = 'Nota fiscal - Listagem'
        self.get_args = ['nf']

        self.table_defs = TableDefs(
            {
                self.CLIENTE: ['Cliente'],
                'nf': ['NF', 'c'],
                'id': ['Cobrança', 'c'],
                'data': ['Data', 'c'],
                'valor': ['Valor cobrança', 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

        self.mount_steps = [
            self.init_query,
            self.filtra_cliente__apelido,
            self.filtra_nf,
            self.filtra_datas,
            self.com_faturamento,
            self.order_query,
            self.exec_query,
            self.context_table,
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

    def filtra_nf(self):
        if self.nf:
            self.query = self.query.filter(
                    nf=self.nf)

    def filtra_datas(self):
        if self.data_de or self.data_ate:
            if self.data_de == self.data_ate:
                self.query = self.query.filter(
                    data=self.data_de)
                return

            if self.data_de:
                self.query = self.query.filter(
                    data__gte=self.data_de)
            if self.data_ate:
                self.query = self.query.filter(
                    data__lte=self.data_ate)

    def context_table(self):
        PrepRows(
            self.data,
        ).str_dash(
            (
                'nf',
            )
        ).process()

        group = [
            'nf',
            self.CLIENTE,
        ]
       
        group_rowspan(self.data, group)
        totalize_grouped_data(
            self.data,
            {
                'group': group,
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

        self.context.update({
            'data': self.data,
            'group': group,
        })
        self.table_defs.hfs_dict_context(self.context)
