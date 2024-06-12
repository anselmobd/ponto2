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

from bordado.forms import FaturamentoForm
from bordado.models import (
    Cliente,
    Cobranca,
)

__all__ = ['FaturamentoView']


class FaturamentoView(LoginRequiredMixin, O2BaseGetPostView):

    # PEDIDO = 'pedidoitemcobranca__pedido_item__pedido'
    # VALOR = 'pedidoitemcobranca__valor'

    def __init__(self):
        super().__init__()
        self.Form_class = FaturamentoForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/faturamento.html'
        self.title_name = 'Faturamento'
        self.table_defs = TableDefs(
            {
                'cliente__apelido': ['Cliente'],
                'nf': ['NF', 'c'],
                'id': ['Cobrança', 'c'],
                'data': ['Data', 'c'],
                # self.PEDIDO: ['Pedido', 'c'],
                # self.VALOR: ['Valor pedido', 'r'],
                'valor': ['Valor cobrança', 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def init_query(self):
        self.query = Cobranca.objects

    def order_query(self):
        self.query = self.query.order_by(
            'cliente__apelido', '-nf', '-data', '-id'
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
                "Filtro definido não seleciona nenhum lançamento")

    def filtra_cliente(self):
        if self.cliente_apelido:
            try:
                Cliente.objects.get(apelido__icontains=self.cliente_apelido)
            except Cliente.DoesNotExist:
                self.form.errors['cliente_apelido'] = [
                    f"Cliente com apelido contendo '{self.cliente_apelido}' "
                    "não existe"]
                # raise StepErrorException("erro do filtro do cliente")
            finally:
                self.query = self.query.filter(
                    cliente__apelido__icontains=self.cliente_apelido)

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
            'cliente__apelido',
        ]
       
        totalize_grouped_data(
            self.data,
            {
                'group': group,
                'sum': ['valor'],
                'descr': {'nf': 'Valor NF:'},
                'global_sum': ['valor'],
                'global_descr': {'nf': 'Total:'},
                'row_if': 'rowspan',
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                # 'flags': ['NO_TOT_1'],
            }
        )
        group_rowspan(self.data, group)

        self.context.update({
            'data': self.data,
            'group': group,
        })
        self.table_defs.hfs_dict_context(self.context)

    def mount_context(self):
        for passo in [
            self.init_query,
            self.filtra_cliente,
            self.com_faturamento,
            self.order_query,
            self.exec_query,
            self.context_table,
        ]:
            try:
                passo()
            except (StopStepsException, StepErrorException) as e:
                self.context['error_msgs'].append(e)
                if isinstance(e, StopStepsException):
                    break
