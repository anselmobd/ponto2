from decimal import Decimal
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, CharField, Value
from django.db.models.functions import Concat

from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefsHBpSD
from o2lib.views.main import (
    totalize_data,
)
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import (
    StepErrorException,
    StopStepsException, 
)

from bordado.forms.analise.cobranca import AnaliseCobrancaForm
from bordado.models import (
    Cliente,
    Cobranca,
)


__all__ = ['AnaliseCobrancaView']


class AnaliseCobrancaView(LoginRequiredMixin, O2BaseGetPostView):

    CLIENTE = 'cliente__apelido'
    VALOR = 'pedidoitemcobranca__valor'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = AnaliseCobrancaForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/analise/cobranca.html'
        self.title_name = 'Analise de cobranças'

        self.totaliza_fields = {
            'c': self.CLIENTE,
            'a': 'data__year',
            'm': 'mes',
        }
        self.table_defs = TableDefsHBpSD(
            {
                self.CLIENTE: ['Cliente', 'c'],
                'data__year': ['Ano', 'a'],
                'mes': ['Mês', 'm'],
                'total': ['Valor', '', 'r'],
                'participacao': ['Participação(%) 	', '', 'r'],
                'acumulada': ['Acumulada(%) 	', '', 'r'],
                'ordem': ['#', '', 'r'],
            },
        )

    def processa_parametros(self):
        self.totaliza_field = self.totaliza_fields[self.totaliza]

    def init_query(self):
        self.query = Cobranca.objects

    def filtra_ano(self):
        if self.ano:
            self.query = self.query.filter(
                data__year=self.ano)

    def filtra_mes(self):
        if self.mes:
            self.query = self.query.filter(
                data__month=self.mes)

    def filtra_cliente(self):

        def do_filtra():
            self.query = self.query.filter(
                **{self.CLIENTE: self.cliente_apelido})
            self.form.data['cliente_apelido'] = self.cliente_apelido

        if self.cliente_apelido:
            try:
                cliente = Cliente.objects.get(
                    apelido__iexact=self.cliente_apelido)
                self.cliente_apelido = cliente.apelido
                do_filtra()
            except Cliente.DoesNotExist as _:
                clientes = Cliente.objects.filter(
                    apelido__icontains=self.cliente_apelido)
                if len(clientes) == 1:
                    self.cliente_apelido = clientes[0].apelido
                    do_filtra()
                elif len(clientes) > 1:
                    apelidos = [cliente.apelido for cliente in clientes]
                    self.form.errors['cliente_apelido'] = [
                        "Mais de um cliente com apelido contendo "
                        f"'{self.cliente_apelido}' "
                        f"({', '.join(apelidos)})"
                    ]
                else:
                    self.form.errors['cliente_apelido'] = [
                        "Cliente com apelido contendo "
                        f"'{self.cliente_apelido}' não existe"
                    ]

    def values_query(self):
        self.query = self.query.annotate(
            mes=Concat(
                'data__year',
                Value('-'),
                'data__month',
                output_field=CharField()
            )
        )
        self.query = self.query.values(
            self.totaliza_field,
        )

    def order_query(self):
        if self.ordem == 'i':
            order_by = self.totaliza_field
        else:
            order_by = '-total'
        self.query = self.query.order_by(order_by)

    def group_query(self):
        self.query = self.query.annotate(
            total=Sum(self.VALOR)
        )

    def exec_query(self):
        self.data = queryset2dictlist(self.query)
        if not self.data:
            raise StopStepsException(
                "Filtro definido não seleciona nenhuma cobrança")

    def totalize_table(self):
        totalize_data(
            self.data,
            {
                'sum': ['total'],
                'descr': {self.totaliza_field: 'Total:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
            }
        )
        total_row = self.data[-1]
        self.valor_total = total_row['total']
        total_row['participacao'] = ''
        total_row['acumulada'] = ''
        total_row['ordem'] = ''

    def prep_table(self):
        valor_acumulado = 0
        for i, row in enumerate(self.data[:-1], start=1):
            row['participacao'] = round(
                row['total'] / self.valor_total * 100, 1)
            valor_acumulado += row['total']
            row['acumulada'] = round(
                valor_acumulado / self.valor_total * 100, 1)
            row['ordem'] = i

    def context_table(self):
        self.context.update({
            'data': self.data,
        })
        self.table_defs.hfs_dict_context(
            self.context,
            bitmap=self.totaliza,
        )

    def mount_context(self):
        self.context.update({
            'show_post': True,
        })
        for passo in [
            self.processa_parametros,
            self.init_query,
            self.filtra_ano,
            self.filtra_mes,
            self.filtra_cliente,
            self.values_query,
            self.group_query,
            self.order_query,
            self.exec_query,
            self.totalize_table,
            self.prep_table,
            self.context_table,
        ]:
            try:
                passo()
            except (StopStepsException, StepErrorException) as e:
                self.context['error_msgs'].append(str(e))
                if isinstance(e, StopStepsException):
                    break
