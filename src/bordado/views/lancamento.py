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

from bordado.forms import LancamentoForm
from bordado.models import (
    Cliente,
    Cobranca,
    Lancamento,
    Pedido,
)

__all__ = ['LancamentoView']


class LancamentoView(LoginRequiredMixin, O2BaseGetPostView):

    PEDIDO = 'cobranca__pedidoitemcobranca__pedido_item__pedido'
    VALOR = 'cobranca__pedidoitemcobranca__valor'
    COMUNICACAO = 'cobranca__comunicacao__descricao'

    def __init__(self):
        super().__init__()
        self.Form_class = LancamentoForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/lancamento.html'
        self.title_name = 'Lançamento'
        self.table_defs = TableDefs(
            {
                'cliente__apelido': ['Cliente'],
                'data': [],
                'informacao': ['Informação', 'c'],
                self.COMUNICACAO: ['Comunicação', 'c'],
                'cobranca__nf': ['NF', 'c'],
                'cobranca': ['Cobrança', 'c'],
                'parcela': [None, 'c'],
                'n_parcelas': ['Nºparcelas', 'c'],
                self.PEDIDO: ['Pedido', 'c'],
                self.VALOR: ['Valor', 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def init_query(self):
        self.query = Lancamento.objects

    def exec_query(self):
        self.data = self.query.values(*self.table_defs.all_fields, 'valor')
        if self.data:
            self.data = queryset2dictlist(self.data)
            ...
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

    def filtra_datas(self):
        if self.data_de:
            self.query = self.query.filter(data__gte=self.data_de)
        if self.data_ate:
            self.query = self.query.filter(data__lte=self.data_ate)

    def filtra_tipo(self):
        if self.tipo_lancamento == '-':
            self.context.update({
                'form_report_excludes': ['tipo_lancamento'],
            })
        elif self.tipo_lancamento == 'c':
            self.query = self.query.filter(cobranca__isnull=False)
        elif self.tipo_lancamento == 'r':
            self.query = self.query.filter(cobranca__isnull=True)

    def context_table(self):
        for row in self.data:
            if row['cobranca']:
                row[self.VALOR] = -row[self.VALOR]
            else:
                row[self.VALOR] = row['valor']

        PrepRows(
            self.data,
        ).str_dash(
            (
                self.PEDIDO,
                'informacao',
                self.COMUNICACAO,
                'cobranca__nf',
                'cobranca',
            )
        ).process()

        group = [
            'cliente__apelido',
            'data',
            'informacao',
            self.COMUNICACAO,
            'cobranca__nf',
            'cobranca',
            'parcela',
            'n_parcelas',
        ]
        sum_fields = [self.VALOR]
        totalize_grouped_data(
            self.data,
            {
                'group': group,
                'sum': sum_fields,
                'descr': {'cliente__apelido': 'Total:'},
                'global_sum': sum_fields,
                'global_descr': {'cliente__apelido': 'Total geral:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
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
            self.filtra_pedido,
            self.filtra_cobranca,
            self.filtra_datas,
            self.filtra_tipo,
            self.exec_query,
            self.context_table,
        ]:
            try:
                passo()
            except (StopStepsException, StepErrorException) as e:
                self.context['error_msgs'].append(e)
                if isinstance(e, StopStepsException):
                    break
