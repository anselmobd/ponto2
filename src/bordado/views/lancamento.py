from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.models.row_field import PrepRows
from o2lib.table_defs import TableDefs
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
    COMUNICACAO = 'cobranca__comunicacao__descricao'

    def __init__(self):
        super().__init__()
        self.Form_class = LancamentoForm
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/lancamento.html'
        self.title_name = 'Lançamento'
        self.table_defs = TableDefs(
            {
                'cliente__apelido': ['Cliente'],
                self.PEDIDO: ['Pedido', 'c'],
                'data': [],
                'informacao': ['Informação', 'c'],
                self.COMUNICACAO: ['Comunicação', 'c'],
                'cobranca__nf': ['NF', 'c'],
                'cobranca': ['Cobrança', 'c'],
                'parcela': [None, 'c'],
                'n_parcelas': ['Nºparcelas', 'c'],
                'valor': [None, 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def init_query(self):
        return Lancamento.objects

    def exec_query(self):
        result = self.query.values(*self.table_defs.all_fields)
        if result:
            return result
        else:
            raise StepErrorException(
                "Filtro definido não seleciona nenhum lançamento")

    def filtra_cliente(self):
        if self.cliente_apelido:
            try:
                Cliente.objects.get(apelido__icontains=self.cliente_apelido)
                self.query = self.query.filter(
                    cliente__apelido__icontains=self.cliente_apelido)
            except Cliente.DoesNotExist:
                raise StepErrorException(
                    f"Cliente com apelido contendo '{self.cliente_apelido}' "
                    "não existe")

    def filtra_pedido(self):
        if self.pedido_numero:
            try:
                pedido = Pedido.objects.get(numero=self.pedido_numero)
                self.query = self.query.filter(
                    **{self.PEDIDO: pedido})
            except Pedido.DoesNotExist:
                raise StepErrorException(
                    f"Pedido {self.pedido_numero} não existe")

    def filtra_cobranca(self):
        if self.cobranca_id:
            try:
                cobranca = Cobranca.objects.get(id=self.cobranca_id)
                self.query = self.query.filter(cobranca=cobranca)
            except Cobranca.DoesNotExist:
                raise StepErrorException(
                    f"Cobranca {self.cobranca_id} não existe")

    def context_table(self):
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

        self.context.update({
            'data': self.data,
        })
        self.table_defs.hfs_dict_context(self.context)

    def mount_context(self):
        if self.steps.do(
            ('query', self.init_query),
            self.filtra_cliente,
            self.filtra_pedido,
            self.filtra_cobranca,
            ('data', self.exec_query),
        ):
            self.context_table()
