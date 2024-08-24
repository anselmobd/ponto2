from datetime import date
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    CharField,
    Sum,
    Value,
)
from django.db.models.fields import (
    TextField,
)
from django.db.models.functions import (
    Cast,
    Concat,
    LPad,
)
from django.http import QueryDict
from django.urls import reverse

from o2lib.form.form_report import form_report
from o2lib.models.dictlist import queryset2dictlist
from o2lib.models.row_field import PrepRows
from o2lib.table_defs import TableDefsHBpSD
from o2lib.views.main import (
    totalize_data,
)
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import StopStepsException

from bordado.forms.analise.cobranca import AnaliseCobrancaForm
from bordado.models import Cobranca
from bordado.views.base.filtro import FiltroParaView


__all__ = ['AnaliseCobrancaView']


class AnaliseCobrancaView(
        LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    CLIENTE = 'cliente__apelido'
    VALOR = 'pedidoitemcobranca__valor'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = AnaliseCobrancaForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/analise/cobranca.html'
        self.title_name = 'Cobrança - Analise'

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

        self.mount_steps = [
            self.processa_parametros,
            self.init_query,
            (self.filtra_valor, ['data__year', 'ano']),
            (self.filtra_valor, ['data__month', 'mes']),
            self.filtra_cliente__apelido,
            self.values_query,
            self.group_query,
            self.order_query,
            self.exec_query,
            self.pre_prep_table,
            self.totalize_table,
            self.prep_table,
            self.context_table,
            self.form_report,
        ]

    def processa_parametros(self):
        self.totaliza_field = self.totaliza_fields[self.totaliza]

    def init_query(self):
        self.query = Cobranca.objects

    def values_query(self):
        self.query = self.query.annotate(
            mes=Concat(
                'data__year',
                Value('-'),
                LPad(
                    Cast('data__month', TextField()),
                    2,
                    Cast(0, TextField()),
                ),
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

    def mount_url_query(self, row):
        qdict = QueryDict('', mutable=True)

        if self.cliente_apelido:
            qdict['cliente_apelido'] = self.cliente_apelido
        else:
            if self.totaliza == 'c':
                qdict['cliente_apelido'] = row[self.CLIENTE]

        ano = None
        mes = None
        if self.ano:
            ano = int(self.ano)
        if self.mes:
            mes = int(self.mes)
        if self.totaliza == 'a':
            ano = row['data__year']
        if self.totaliza == 'm':
            ano_mes = row['mes'].split('-')
            ano = int(ano_mes[0])
            mes = int(ano_mes[1])
        data_de = date(ano, mes if mes else 1, 1)
        dia = 31
        while dia != 0:
            try:
                data_ate = date(ano, mes if mes else 12, dia)
                break
            except ValueError as _:
                dia -= 1
        qdict['data_de'] = data_de
        qdict['data_ate'] = data_ate

        return qdict.urlencode()

    def pre_prep_table(self):
        PrepRows(
            self.data,
        ).none(
            'total', 0
        ).process()


    def prep_table(self):
        valor_acumulado = 0
        for i, row in enumerate(self.data[:-1], start=1):
            row['participacao'] = round(
                row['total'] / self.valor_total * 100, 1)
            valor_acumulado += row['total']
            row['acumulada'] = round(
                valor_acumulado / self.valor_total * 100, 1)
            row['ordem'] = i

            row[f"{self.totaliza_field}|TARGET"] = 'blank'
            row[f"{self.totaliza_field}|A"] = "?".join([
                reverse('bordado:listagem_cobranca', args=[]),
                self.mount_url_query(row),
            ])

    def context_table(self):
        self.context.update({
            'data': self.data,
        })
        self.table_defs.hfs_dict_context(
            self.context,
            bitmap=self.totaliza,
        )

    def form_report(self):
        self.context.update({
            'form_report': form_report(
                self.form,
                field_modifier={'ano': str}
            ),
        })
