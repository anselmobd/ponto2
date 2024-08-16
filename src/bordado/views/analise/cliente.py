from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.codes.cnpj import CNPJ
from o2lib.models.dictlist import queryset2dictlist
from o2lib.models.row_field import PrepRows
from o2lib.table_defs import TableDefsH
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import StopStepsException

from bordado.forms.analise.cliente import AnaliseClienteForm
from bordado.models import Cliente
from bordado.queries.lancamento.totalizador import get_totais_lancamentos
from bordado.queries.pedido.totalizador import get_totais_pedidos
from bordado.views.base.filtro import FiltroParaView


__all__ = ['AnaliseClienteView']


class AnaliseClienteView(
        LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = AnaliseClienteForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = "bordado/analise/cliente.html"
        self.title_name = "Cliente - Analise"
        self.get_args = ['apelido']
        self.get_vars2form = True

        self.lista_clientes_defs = TableDefsH(
            {
                'apelido': None,
                'nome': 'Nome/Razão Social',
                'fantasia': 'Nome Fantasia',
                'cnpj': "CNPJ",
            }
        )
        self.lista_clientes_extra_fields = [
            'apelido_slug',
            'cnpj9',
            'cnpj4',
            'cnpj2',
        ]
        self.cliente_end1_defs = TableDefsH(
            {
                'logradouro': None,
                'numero': "Número",
                'complemento': None,
            }
        )
        self.cliente_end2_defs = TableDefsH(
            {
                'bairro': None,
                'cidade': None,
                'uf': 'UF',
                'cep': "CEP",
            }
        )
        self.totais_defs = TableDefsH(
            {
                'fechado': 'Pedidos não cobrados',
                'cobrado': 'Cobranças',
                'recebido': 'Recebimentos',
                'saldo': None,
            }
        )

        self.mount_steps = [
            # Mostra lista de clientes ou nomes do cliente
            (self.init_query_cliente, 'query_clientes'),
            (self.filtra_cliente__apelido, [
                'apelido', 'apelido', 'query_clientes', False]),
            self.values_query_clientes,
            self.order_query_clientes,
            self.exec_query_clientes,
            self.prep_clientes_data,
            self.context_list_clientes,

            # Mostra dados do cliente
            (self.init_query_cliente, 'query_cliente'),
            (self.filtra_cliente__apelido, [
                'apelido', 'apelido', 'query_cliente']),
            self.values_query_cliente,
            self.exec_query_cliente,
            self.prep_cliente_data,
            self.context_capa_cliente,

            # Mostra totais de pedidos
            self.totais_pedidos,
        ]

    def init_query_cliente(self):
        return Cliente.objects

    def values_query_clientes(self):
        self.query_clientes = self.query_clientes.values(
            *[
                *self.lista_clientes_defs.get_fields(exclude=['cnpj']),
                *self.lista_clientes_extra_fields,
            ]
        )

    def values_query_cliente(self):
        self.query_cliente = self.query_cliente.values(
            *[
                'id',
                *self.cliente_end1_defs.all_fields,
                *self.cliente_end2_defs.all_fields,
            ]
        )

    def order_query_clientes(self):
        self.query_clientes = self.query_clientes.order_by('apelido')

    def exec_query_clientes(self):
        self.clientes_data = queryset2dictlist(self.query_clientes)

    def exec_query_cliente(self):
        self.cliente_data = queryset2dictlist(self.query_cliente)

    def prep_clientes_data(self):
        PrepRows(
            self.clientes_data,
        ).none(
            (
                'cnpj9',
                'cnpj4',
                'cnpj2',
            ), 0
        ).a_blank(
            'apelido', 'bordado:analise_cliente', ['apelido_slug'],
        ).process()
        for row in self.clientes_data:
            if row['cnpj9']:
                row['cnpj'] = CNPJ(row['cnpj9'], row['cnpj4'], row['cnpj2'])
            else:
                row['cnpj'] = "-"

    def prep_cliente_data(self):
        PrepRows(
            self.cliente_data,
        ).none(
            'numero', ''
        ).process()

    def context_list_clientes(self):
        self.context.update({
            'clientes_data': self.clientes_data,
        })
        self.lista_clientes_defs.hfs_dict_context(
            self.context,
        )
        if len(self.clientes_data) != 1:
            raise StopStepsException(
                "Lista clientes")

    def context_capa_cliente(self):
        self.context.update({
            'cliente_data': self.cliente_data,
        })
        self.cliente_end1_defs.hfs_dict_context(
            self.context,
            sufixo='end1_',
        )
        self.cliente_end2_defs.hfs_dict_context(
            self.context,
            sufixo='end2_',
        )

    def totais_pedidos(self):
        totais = get_totais_pedidos(self.cliente_data[0]['id'])
        totais_lancamentos = get_totais_lancamentos(self.cliente_data[0]['id'])
        totais.update(totais_lancamentos)
        totais['saldo'] = totais['recebido'] - totais['cobrado'] - totais['fechado']

        config_totais = {
            'data': [totais],
            'data_title': "Posição financeira",
        }
        self.totais_defs.hfs_dict_context(config_totais)

        self.context.update({
            'totais': config_totais,
        })
