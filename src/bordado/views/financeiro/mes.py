import operator
from collections import defaultdict
from decimal import Decimal
from pprint import pprint

from dateutil.relativedelta import relativedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import QueryDict
from django.urls import reverse

from o2lib.date import strymd2date, yesterday, ymd
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
        self.title_name = "Financeiro - Clientes / Meses"

        self.mount_steps = [
            self.mount_meses,
            self.mount_fields_meses,
            self.mount_row_zerada,
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
            return f'{name}_geral'

    def mount_meses(self):
        self.meses = [(None, None)]
        ano, mes = self.ano, self.mes
        for _ in range(self.num_meses):
            self.meses.append((ano, mes))
            ano, mes = self.ano_mes_anterior(ano, mes)

    def mount_fields_meses(self):
        self.fields_meses = []
        for ano, mes in self.meses:
            tipos = ['saldo', 'recebido', 'cobrado', 'fechado']
            if (not ano) and (self.num_meses == 0):
                tipos.extend(['areceber', 'saldo_atual'])
            for tipo in tipos:
                self.fields_meses.append(self.fname(tipo, ano, mes))

    def mount_row_zerada(self):
        self.mount_row_zerada = {}
        for field in self.fields_meses:
            self.mount_row_zerada[field] = Decimal('0.00')

    def valores_inteiros(self, row):
        for field in self.fields_meses:
            row[field] = int(row[field])

    def spaces(self, row):
        space = False
        for ano, mes in self.meses[::-1]:
            if space:
                row[self.fname('space', ano, mes)] = ' '
            else:
                space = True
        return row

    def decimal0(self):
        return Decimal('0.00')

    def decimal0_dict(self):
        return defaultdict(self.decimal0)

    def add_to_dictdata(
            self, dictlist, dictdata, key, callable_default=None):
        if not callable_default:
            callable_default = self.decimal0_dict
        for row in dictlist:
            if row[key] not in dictdata:
                dictdata[row[key]] = callable_default()
            dictdata[row[key]].update(row)

    def get_valores_dict_mes(self, ano=None, mes=None, filtro=None):
        valores_dict = {}

        pedido_mes = get_pedido_financeiro_mes(
            ano=ano,
            mes=mes,
            group_by='cliente'
        )
        self.add_to_dictdata(pedido_mes, valores_dict, 'cliente__apelido')

        lancamento_mes = get_lancamento_financeiro_mes(
            ano=ano,
            mes=mes,
            group_by='cliente',
            separa_areceber=(self.num_meses==0),
        )
        self.add_to_dictdata(lancamento_mes, valores_dict, 'cliente__apelido')

        for _, row in valores_dict.items():
            row['saldo'] = (
                row['recebido']
                - row['cobrado']
                - row['fechado']
            )
            if self.num_meses == 0:
                row['saldo_atual'] = row['saldo']
                row['saldo'] = (
                    row['recebido']
                    - row['cobrado']
                    - row['fechado']
                    - row['areceber']
                )

        if callable(filtro):
            return {
                key: row
                for key, row in valores_dict.items()
                if filtro(row)
            }
        else:
            return valores_dict

    def filtro_tem_saldo(self, row):
        return row['saldo']

    def dict_de_para(self, de, para, regra):
        for de_key, para_key in regra.items():
            para[para_key] = de[de_key]

    def mount_totais_pedidos_dict_meses(self):
        self.meses_dict = {}
        for ano, mes in self.meses:
            filtro = None if ano else self.filtro_tem_saldo
            tipos = ['saldo', 'recebido', 'cobrado', 'fechado']
            if (not ano) and (self.num_meses == 0):
                tipos.extend(['areceber', 'saldo_atual'])
            valores_dict = self.get_valores_dict_mes(ano, mes, filtro)
            translate_fields = {
                tipo: self.fname(tipo, ano, mes)
                for tipo in tipos
            }
            for cliente, row in valores_dict.items():
                if cliente not in self.meses_dict:
                    self.meses_dict[cliente] = self.mount_row_zerada.copy()
                self.dict_de_para(
                    row,
                    self.meses_dict[cliente],
                    translate_fields,
                )

    def mount_totais_pedidos(self):
        self.totais_pedidos = []
        for cliente, row in self.meses_dict.items():
            row['cliente__apelido'] = cliente
            self.totais_pedidos.append(row)
        if not self.totais_pedidos:
            raise StopStepsException(
                "Nada selecionado")
        for row in self.totais_pedidos:
            self.valores_inteiros(row)
            self.spaces(row)

    def sort_totais_pedidos(self):
        if self.ordem == 'c':
            self.totais_pedidos.sort(
                key=operator.itemgetter('cliente__apelido'))
        elif self.ordem == 'f':
            self.totais_pedidos.sort(
                key=operator.itemgetter(
                    self.fname('saldo', *self.meses[1])))
        elif self.ordem == 'i':
            self.totais_pedidos.sort(
                key=operator.itemgetter(
                    self.fname('saldo', *self.meses[-1])))
        else:
            self.totais_pedidos.sort(
                key=operator.itemgetter('saldo_geral', 'cliente__apelido'))

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
                [('Pedidos<br/>abertos',), 'r amarelo']
            definicao[self.fname('cobrado', ano, mes)] = \
                [('<br/>Cobrado',), 'r vermelho']
            definicao[self.fname('recebido', ano, mes)] = \
                [('<br/>Recebido',), 'r verde']
            if ano and mes:
                definicao[self.fname('saldo', ano, mes)] = \
                    [(f'{mes:02d}/{ano}<br/>Saldo',), 'r azul']
            else:
                if self.num_meses == 0:
                    definicao[self.fname('saldo_atual', ano, mes)] = \
                        [('Atual<br/>Saldo',), 'r azulao']
                    definicao[self.fname('areceber', ano, mes)] = \
                        [('<br/>A receber',), 'r vermelho']
                definicao[self.fname('saldo', ano, mes)] = \
                    [('Geral<br/>Saldo',), 'r azulao']
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

    def mount_url_query(
            self, row, ano, mes, cobranca='n', apresentacao='p',
            data_de='entrega_de', data_ate='entrega_ate'):
        qdict = QueryDict('', mutable=True)
        qdict['cliente_apelido'] = row['cliente__apelido']
        qdict['cobranca'] = cobranca
        qdict['apresentacao'] = apresentacao
        if ano and mes:
            qdict[data_de] = f'{ano}-{mes:02d}-01'
            dt = strymd2date(
                f'{ano}-{mes}-01'
            )
            dt = dt+relativedelta(months=+1)
            qdict[data_ate] = ymd(yesterday(dt))
        return qdict.urlencode()

    def prep_data(self):
        PrepRows(
            self.totais_pedidos,
        ).a_blank(
            'cliente__apelido', 'bordado:analise_cliente', ['cliente__apelido'],
        ).process()

        for row in self.totais_pedidos:
            for ano, mes in self.meses:
                field = self.fname('fechado', ano, mes)
                if row[field]:
                    row[f"{field}|TARGET"] = 'blank'
                    row[f"{field}|A"] = "?".join([
                        reverse('bordado:listagem_pedido'),
                        self.mount_url_query(row, ano, mes),
                    ])
                field = self.fname('cobrado', ano, mes)
                if row[field]:
                    row[f"{field}|TARGET"] = 'blank'
                    row[f"{field}|A"] = "?".join([
                        reverse('bordado:listagem_pedido'),
                        self.mount_url_query(
                            row, ano, mes, cobranca='c', apresentacao='c',
                            data_de='cobranca_de', data_ate='cobranca_ate',
                        ),
                    ])

    def calcula_totalizador(self):
        totalize_data(
            self.totais_pedidos,
            {
                'sum': self.fields_meses,
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
