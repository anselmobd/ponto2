from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.models.row_field import PrepRows
from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefsHBpSD
from o2lib.views.main import (
    group_rowspan,
    totalize_data,
)
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import (
    StepErrorException,
    StopStepsException, 
)

from bordado.forms.listagem.lancamento import LancamentoForm
from bordado.models import (
    Cliente,
    Cobranca,
    Lancamento,
    Pedido,
)
from bordado.views.base.filtro import FiltroParaView

__all__ = ['LancamentoView']


class LancamentoView(LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    CLIENTE = 'cliente__apelido'
    PEDIDO = 'cobranca__pedidoitemcobranca__pedido_item__pedido'
    VALOR = 'cobranca__pedidoitemcobranca__valor'
    COMUNICACAO = 'cobranca__comunicacao__descricao'

    def __init__(self):
        super().__init__()
        self.Form_class = LancamentoForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/listagem/lancamento.html'
        self.title_name = "Lançamento - Listagem"
        self.table_defs = TableDefsHBpSD(
            {
                self.CLIENTE: ['Cliente'],
                'data': [],
                'informacao': ['Informação', '', 'c'],
                self.COMUNICACAO: ['Comunicação', '', 'c'],
                'cobranca__nf': ['NF', '', 'c'],
                'cobranca': ['Cobrança', '', 'c'],
                'parcela': [None, '', 'c'],
                'valor': ['Valor cobrança', '', 'r'],
                self.PEDIDO: ['Pedido', '-c', 'c'],
                self.VALOR: ['Valor pedido', '-c', 'r'],
            },
        )
        self.extra_fields = [
            'cobranca__informacao',
            'n_parcelas',
        ]

        self.mount_steps = [
            self.init_query,
            self.filtra_cliente__apelido,
            self.filtra_pedido,
            self.filtra_cobranca,
            (self.filtra_valor_de_ate, ['data', 'data_de', 'data_ate']),
            self.filtra_tipo,
            self.exec_query,
            self.prep_table,
            self.group_table,
            self.totalize_table,
            self.context_table,
        ]

    def init_query(self):
        self.query = Lancamento.objects

    def exec_query(self):
        self.data = self.query.values(
            *self.table_defs.all_fields, *self.extra_fields)
        if self.data:
            self.data = queryset2dictlist(self.data)
        else:
            raise StopStepsException(
                "Filtro definido não seleciona nenhum lançamento")

    def filtra_pedido(self):
        if self.pedido_numero:
            try:
                Pedido.objects.get(numero=self.pedido_numero)
            except Pedido.DoesNotExist:
                self.form.errors['pedido_numero'] = [
                    f"Pedido {self.pedido_numero} não existe"]
            finally:
                self.query = self.query.filter(
                    **{self.PEDIDO: self.pedido_numero})

    def filtra_cobranca(self):
        if self.cobranca_id:
            try:
                Cobranca.objects.get(id=self.cobranca_id)
            except Cobranca.DoesNotExist:
                self.form.errors['cobranca_id'] = [
                    f"Cobranca {self.cobranca_id} não existe"]
            finally:
                self.query = self.query.filter(cobranca_id=self.cobranca_id)

    def filtra_tipo(self):
        if self.tipo_lancamento == '-':
            self.context.update({
                'form_report_excludes': ['tipo_lancamento'],
            })
        elif self.tipo_lancamento == 'c':
            self.query = self.query.filter(cobranca__isnull=False)
        elif self.tipo_lancamento == 'r':
            self.query = self.query.filter(cobranca__isnull=True)

    def prep_table(self):
        for row in self.data:
            if row['cobranca']:
                row[self.VALOR] = -row[self.VALOR]
                row['informacao'] = row['cobranca__informacao']
                row['parcela'] = f"{row['parcela']}/{row['n_parcelas']}"
            else:
                if self.tipo_lancamento != 'r':
                    row['|STYLE'] = 'color: darkgreen;'

        PrepRows(
            self.data,
        ).str_dash(
            (
                self.PEDIDO,
                'informacao',
                self.COMUNICACAO,
                'cobranca__nf',
                'cobranca',
                self.VALOR,
                'parcela',
            )
        ).a_blank(
            'cobranca', 'bordado:cobranca'
        ).process()

    def group_table(self):
        if self.tipo_lancamento != 'r':
            self.group = [
                self.CLIENTE,
                'data',
                'informacao',
                self.COMUNICACAO,
                'cobranca__nf',
                'cobranca',
                'parcela',
                'n_parcelas',
                'valor',
            ]
            group_rowspan(self.data, self.group)
        else:
            self.group = []
        
    def totalize_table(self):
        totalize_config = {
            'sum': ['valor'],
            'descr': {self.CLIENTE: 'Total:'},
            # 'row_if': 'rowspan',
            'row_style':
                "font-weight: bold;"
                "background-image: linear-gradient(#DDD, white);",
            'flags': ['NO_TOT_1'],
        }
        if self.tipo_lancamento != 'r':
            totalize_config['row_if'] = 'rowspan'
        totalize_data(self.data, totalize_config)

    def context_table(self):
        self.context.update({
            'data': self.data,
            'group': self.group,
        })
        self.table_defs.hfs_dict_context(
            self.context,
            bitmap=self.tipo_lancamento,
        )
