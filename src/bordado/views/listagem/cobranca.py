from decimal import Decimal
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

from bordado.forms.listagem.cobranca import CobrancaForm
from bordado.models import (
    Cliente,
    Cobranca,
)

__all__ = ['CobrancaView']


class CobrancaView(LoginRequiredMixin, O2BaseGetPostView):

    CLIENTE = 'cliente__apelido'
    COMUNICACAO = 'comunicacao__descricao'
    PEDIDO = 'pedidoitemcobranca__pedido_item__pedido'
    QUANTIDADE = 'pedidoitemcobranca__pedido_item__quantidade'
    BORDADO_NOME = 'pedidoitemcobranca__pedido_item__bordado__nome'
    BORDADO_CODIGO = 'pedidoitemcobranca__pedido_item__bordado__codigo'
    VALOR = 'pedidoitemcobranca__valor'

    def __init__(self, *args, **kwargs):
        super(CobrancaView, self).__init__(*args, **kwargs)
        self.Form_class = CobrancaForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/cobranca.html'
        self.title_name = "Cobrança - Listagem"
        self.get_args = ['numero']
        self.get_vars2form = True

        self.table_defs = TableDefs(
            {
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
                self.VALOR: ['Valor pedido', 'r'],
                'usuario__username': ["Usuário"],
                'quando': [],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

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

    def filtra_numero_cobranca(self):
        if self.numero:
            self.query = self.query.filter(
                    id=self.numero)

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
                else:
                    if len(clientes) > 1:
                        apelidos = [cliente.apelido for cliente in clientes]
                        msg_erro = (
                            "Mais de um cliente com apelido contendo "
                            f"'{self.cliente_apelido}' "
                            f"({', '.join(apelidos)})"
                        )
                    else:
                        msg_erro = (
                            "Cliente com apelido contendo "
                            f"'{self.cliente_apelido}' não existe"
                        )
                    self.form.errors['cliente_apelido'] = [msg_erro]
                    raise StopStepsException("Filtro de cliente mal definido")

    def context_table(self):
        PrepRows(
            self.data,
        ).str_dash(
            (
                'nf',
                'informacao',
                'parcelamento',
                self.BORDADO_CODIGO,
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

    def mount_context(self):
        self.context.update({
            'show_post': True,
        })
        self.do_steps(
            [
                self.init_query,
                self.filtra_cliente,
                self.filtra_numero_cobranca,
                self.filtra_datas,
                self.order_query,
                self.exec_query,
                self.context_table,
            ],
        )
