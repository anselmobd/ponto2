import operator
from decimal import Decimal
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from o2lib.form.form_report import form_report
from o2lib.models.row_field import PrepRows
from o2lib.table_defs import TableDefsHpS
from o2lib.views.base.exception import StopStepsException
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.totalize import totalize_data

from bordado.forms.financeiro.mes import FinanceiroMesForm
from bordado.queries.lancamento.financeiro_mes import \
    get_lancamento_financeiro_mes
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
        self.title_name = "Financeiro - Por 3 mêses / Clientes"

        self.mount_steps = [
            self.mount_meses,
            self.mount_fields_meses,
            self.mount_totais_pedidos_dict_meses,
            self.mount_totais_pedidos,
            self.sort_totais_pedidos,
            self.mount_totais_defs,
            self.prep_data,
            self.calcula_totalizador,
            self.context_table,
            self.form_report,
        ]

    def ano_mes_anterior(self, ano, mes):
        mes -= 1
        if mes == 0:
            mes = 12
            ano -= 1
        return ano, mes

    def fname(self, name, ano, mes):
        if ano and mes:
            return f'{name}_{ano}_{mes:02d}'
        else:
            return f'{name}_total'

    def mount_meses(self):
        self.meses = [(None, None)]
        ano, mes = self.ano, self.mes
        for _ in range(3):
            self.meses.append((ano, mes))
            ano, mes = self.ano_mes_anterior(ano, mes)

    def mount_fields_meses(self):
        self.fields_meses = []
        for ano, mes in self.meses:
            for tipo in ['saldo', 'recebido', 'cobrado', 'fechado']:
                self.fields_meses.append(self.fname(tipo, ano, mes))

    def row_zerada(self):
        row = {}
        for field in self.fields_meses:
            row[field] = Decimal('0.00')
        return row

    def calc_saldos(self, row):
        for ano, mes in self.meses:
            saldo = (
                row[self.fname('recebido', ano, mes)]
                - row[self.fname('cobrado', ano, mes)]
                - row[self.fname('fechado', ano, mes)]
            )
            row[self.fname('saldo', ano, mes)] = saldo
        return row

    def valores_inteiros(self, row):
        for field in self.fields_meses:
            row[field] = int(row[field])
        space = False
        for ano, mes in self.meses[::-1]:
            if space:
                row[self.fname('space', ano, mes)] = ' '
            else:
                space = True
        return row

    def get_totais_pedidos_dict_mes(self, ano, mes):
        dados = get_pedido_financeiro_mes(
            ano=ano,
            mes=mes,
            group_by='cliente'
        )
        dados_dict = {}
        for row in dados:
            dados_dict[row['cliente__apelido']] = {
                self.fname('fechado', ano, mes): row['fechado'],
                self.fname('cobrado', ano, mes): row['cobrado'],
            }
        return dados_dict

    def get_totais_lancamento_dict_mes(self, ano, mes):
        dados = get_lancamento_financeiro_mes(
            ano=ano,
            mes=mes,
            group_by='cliente'
        )
        dados_dict = {}
        for row in dados:
            dados_dict[row['cliente__apelido']] = {
                self.fname('cobrado', ano, mes): row['cobrado'],
                self.fname('recebido', ano, mes): row['recebido'],
            }
        return dados_dict

    def mount_totais_pedidos_dict_meses(self):
        row_zerada = self.row_zerada()
        self.totais_pedidos_dict = {}
        for ano_mes in self.meses:
            pedido_mes = self.get_totais_pedidos_dict_mes(*ano_mes)
            lancamento_mes = self.get_totais_lancamento_dict_mes(*ano_mes)
            for fonte in [pedido_mes, lancamento_mes]:
                for cliente, row in fonte.items():
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
        for row in self.totais_pedidos:
            self.calc_saldos(row)
            self.valores_inteiros(row)

    def sort_totais_pedidos(self):
        self.totais_pedidos.sort(
            key=operator.itemgetter('saldo_total', 'cliente__apelido'))

    def mount_totais_defs(self):
        definicao = {
            'cliente__apelido': ['Cliente'],
        }
        space = False
        for ano, mes in self.meses[::-1]:
            if space:
                definicao[self.fname('space', ano, mes)] = ' '
            else:
                space = True
            definicao[self.fname('fechado', ano, mes)] = \
                [('<br/>Pedido',), 'r amarelo']
            definicao[self.fname('cobrado', ano, mes)] = \
                [('<br/>Cobrado',), 'r vermelho']
            definicao[self.fname('recebido', ano, mes)] = \
                [('<br/>Recebido',), 'r verde']
            if ano and mes:
                definicao[self.fname('saldo', ano, mes)] = \
                    [(f'{mes:02d}/{ano}<br/>Saldo',), 'r azul']
            else:
                definicao[self.fname('saldo', ano, mes)] = \
                    [('Total<br/>Saldo',), 'r azulao']
        self.totais_defs = TableDefsHpS(
            definicao,
            style={
                'amarelo': "background-color: khaki;",
                'vermelho': "background-color: lightsalmon;",
                'verde': "background-color: lightgreen;",
                'azul': "background-color: lightblue;",
                'azulao': "background-color: lightskyblue;",
            },
        )

    def prep_data(self):
        PrepRows(
            self.totais_pedidos,
        ).a_blank(
            'cliente__apelido', 'bordado:analise_cliente', ['cliente__apelido'],
        ).process()

    def calcula_totalizador(self):
        totalize_data(
            self.totais_pedidos,
            {
                'sum': [
                    field for field in self.fields_meses
                    if not field.startswith('saldo')
                ],
                'descr': {'cliente__apelido': 'Totais'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
            }
        )
        self.total_geral = self.totais_pedidos.pop()
        self.totais_pedidos.insert(0, self.total_geral)

    def context_table(self):
        config_totais = {
            'data': self.totais_pedidos,
            'thclass': 'sticky',
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
