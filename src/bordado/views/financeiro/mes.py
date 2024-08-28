from decimal import Decimal
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

        self.mount_steps = [
            self.mount_meses,
            self.mount_totais_pedidos_dict_meses,
            self.mount_totais_pedidos,
            self.mount_totais_defs,
            self.context_tatle,
            self.form_report,
        ]

    def ano_mes_anterior(self, ano, mes):
        mes -= 1
        if mes == 0:
            mes = 12
            ano -= 1
        return ano, mes

    def mount_meses(self):
        self.meses = {}
        ano, mes = self.ano, self.mes
        for _ in range(3):
            self.meses[(ano, mes)] = {
                'ano': ano,
                'mes': mes,
                'tupla': (ano, mes),
                '_': f'{ano}_{mes:02d}',
                '/': f'{mes:02d}/{ano}',
            }
            ano, mes = self.ano_mes_anterior(ano, mes)

    def get_totais_pedidos_dict_mes(self, ano, mes):
        dados = get_pedido_financeiro_mes(
            ano=ano,
            mes=mes,
            group_by='cliente'
        )
        dados_dict = {}
        for row in dados:
            dados_dict[row['cliente__apelido']] = {
                f'cobrado_{ano}_{mes}': row['cobrado'],
                f'fechado_{ano}_{mes}': row['fechado'],
            }
        return dados_dict

    def row_zerada(self):
        row = {}
        for ano_mes in self.meses:
            ano, mes = ano_mes
            row[f'cobrado_{ano}_{mes}'] = Decimal('0.00')
            row[f'fechado_{ano}_{mes}'] = Decimal('0.00')
        return row

    def mount_totais_pedidos_dict_meses(self):
        row_zerada = self.row_zerada()
        self.totais_pedidos_dict = {}
        for ano_mes in self.meses:
            dict_mes = self.get_totais_pedidos_dict_mes(
                *self.meses[ano_mes]['tupla'])
            for cliente, row in dict_mes.items():
                if cliente not in self.totais_pedidos_dict:
                    self.totais_pedidos_dict[cliente] = row_zerada.copy()
                self.totais_pedidos_dict[cliente].update(row)


    def mount_totais_pedidos(self):
        self.totais_pedidos = []
        for cliente, row in self.totais_pedidos_dict.items():
            row['cliente__apelido'] = cliente
            self.totais_pedidos.append(row)
        if not self.totais_pedidos:
            raise StopStepsException(
                "Nada selecionado")

    def mount_totais_defs(self):
        definicao = {
            'cliente__apelido': ['Cliente'],
            # 'recebido': ['Recebimentos', 'r'],
            # 'saldo': ['', 'r'],
        }
        for ano_mes in list(self.meses.keys())[::-1]:
            ano, mes = ano_mes
            definicao[f'fechado_{ano}_{mes}'] = \
                [f'({mes}/{ano})Pedidos', 'r']
            definicao[f'cobrado_{ano}_{mes}'] = \
                [f'({mes}/{ano})Cobranças', 'r']
        self.totais_defs = TableDefsHpS(definicao)

    def context_tatle(self):
        config_totais = {
            'data': self.totais_pedidos,
            'data_title': "Posição financeira por cliente",
        }
        self.totais_defs.hfs_dict_context(config_totais)

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
