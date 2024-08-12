from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefsHBpSD
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

        self.table_defs = TableDefsHBpSD(
            {
                'apelido': ["Apelido"],
                'nome': ['Nome/Razão Social'],
                'fantasia': ['Nome Fantasia'],
            },
        )

        self.mount_steps = [
            self.init_query,
            (self.filtra_cliente__apelido, ['apelido', 'apelido']),
            self.values_query,
            self.order_query,
            self.exec_query,
            self.context_table,
        ]

    def init_query(self):
        self.query = Cliente.objects

    def values_query(self):
        self.query = self.query.values(
            *self.table_defs.all_fields)

    def order_query(self):
        self.query = self.query.order_by('apelido')

    def exec_query(self):
        self.data = queryset2dictlist(self.query)
        if not self.data:
            raise StopStepsException(
                "Filtro definido não seleciona nenhum cliente")

    def context_table(self):
        self.context.update({
            'data': self.data,
        })
        self.table_defs.hfs_dict_context(
            self.context,
        )
        if len(self.data) > 1:
            raise StopStepsException(
                "Apenas lista clientes")
