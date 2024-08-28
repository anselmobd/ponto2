from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.form.form_report import form_report
from o2lib.table_defs import TableDefsHpS
from o2lib.views.base.exception import StopStepsException
from o2lib.views.base.get_post import O2BaseGetPostView

from bordado.forms.financeiro.mes import FinanceiroMesForm
from bordado.queries.pedido.financeiro_mes import get_pedido_financeiro_mes
from bordado.views.base.filtro import FiltroParaView


__all__ = ['FinanceiroMesView']


class FinanceiroMesView(
        LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = FinanceiroMesForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.template_name = "bordado/financeiro/mes.html"
        self.title_name = "Financeiro - Mês"

        self.totais_mes_defs = TableDefsHpS(
            {
                'cliente__apelido': ['Cliente apelido'],
                'fechado': ['Pedidos não cobrados', 'r'],
                'cobrado': ['Cobranças', 'r'],
                # 'recebido': ['Recebimentos', 'r'],
                # 'saldo': ['', 'r'],
            }
        )

        self.mount_steps = [
            self.totais_por_cliente,
            self.context_tatle,
            self.form_report,
        ]

    def totais_por_cliente(self):
        self.totais_pedidos = get_pedido_financeiro_mes(
            ano=self.ano,
            mes=self.mes,
            group_by='cliente'
        )
        pprint(self.totais_pedidos)
        if not self.totais_pedidos:
            raise StopStepsException(
                "Nada selecionado")


    def context_tatle(self):
        config_totais = {
            'data': self.totais_pedidos,
            'data_title': "Posição financeira por cliente",
        }
        self.totais_mes_defs.hfs_dict_context(config_totais)

        self.context.update({
            'totais_por_mes': config_totais,
        })

    def form_report(self):
        self.context.update({
            'form_report': form_report(
                self.form,
                field_modifier={'ano': str}
            ),
        })
