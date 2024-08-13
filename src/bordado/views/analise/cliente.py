from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefsH
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import StopStepsException

from bordado.forms.analise.cliente import AnaliseClienteForm
from bordado.models import Cliente
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
        self.template_name = 'bordado/analise/cliente.html'
        self.title_name = 'Cliente - Analise'

        self.lista_clientes_nomes_defs = TableDefsH(
            {
                'apelido': ["Apelido"],
                'nome': ['Nome/Razão Social'],
                'fantasia': ['Nome Fantasia'],
            }
        )
        self.lista_clientes_numeros_defs = TableDefsH(
            {
                'cnpj9': ["CNPJ (raiz)"],
                'cnpj4': ["CNPJ (filial)"],
                'cnpj2': ["CNPJ (dígitos)"],
                'cep': ["CEP"],
            }
        )

        self.mount_steps = [
            self.init_query_cliente,
            (self.filtra_cliente__apelido, [
                'apelido', 'apelido', 'query_cliente']),
            self.values_query_cliente,
            self.order_query_cliente,
            self.exec_query_cliente,
            self.context_list_cliente,
            # Mostra dados de 1 cliente
            self.init_query_cliente,
            (self.filtra_cliente__apelido, [
                'apelido', 'apelido', 'query_cliente']),
        ]

    def init_query_cliente(self):
        self.query_cliente = Cliente.objects

    def values_query_cliente(self):
        self.query_cliente = self.query_cliente.values(
            *[
                *self.lista_clientes_nomes_defs.all_fields,
                *self.lista_clientes_numeros_defs.all_fields,
            ]
        )

    def order_query_cliente(self):
        self.query_cliente = self.query_cliente.order_by('apelido')

    def exec_query_cliente(self):
        self.cliente_data = queryset2dictlist(self.query_cliente)
        if not self.cliente_data:
            raise StopStepsException(
                "Filtro definido não seleciona nenhum cliente")

    def context_list_cliente(self):
        self.context.update({
            'cliente_data': self.cliente_data,
        })
        self.lista_clientes_nomes_defs.hfs_dict_context(
            self.context,
        )
        if len(self.cliente_data) > 1:
            raise StopStepsException(
                "Apenas lista clientes")

        self.lista_clientes_numeros_defs.hfs_dict_context(
            self.context,
            sufixo='num_',
        )
