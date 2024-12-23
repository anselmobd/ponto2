import datetime
from decimal import Decimal
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, ExpressionWrapper, DecimalField

from o2lib.form.form_report import form_report
from o2lib.models.row_field import PrepRows
from o2lib.models.dictlist import queryset2dictlist
from o2lib.number import decimal_proporcional
from o2lib.table_defs import TableDefsHBpSD
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import StopStepsException
from o2lib.views.group import group_rowspan
from o2lib.views.totalize import totalize_data
from o2lib.views.paginator import list_paginator_basic

from bordado.forms.listagem.pedido import ListagemPedidoForm
from bordado.models import Pedido
from bordado.views.base.filtro import FiltroParaView


__all__ = ['ListagemPedidoView']


class ListagemPedidoView(LoginRequiredMixin, O2BaseGetPostView, FiltroParaView):

    AJUSTE = 'pedidoitem__ajuste'
    BORDADO_CODIGO = 'pedidoitem__bordado__codigo'
    BORDADO_NOME = 'pedidoitem__bordado__nome'
    OBSERVACAO = 'pedidoitem__observacao'
    CLIENTE = 'cliente__apelido'
    COBRANCA = 'pedidoitem__cobrancas__cobranca'
    COBRANCA_PEDIDO_VALOR = 'pedidoitem__cobrancas__valor'
    COBRANCA_VALOR = 'pedidoitem__cobrancas__cobranca__valor'
    PARCELA_PEDIDO_VALOR = 'parcela_pedido_valor'
    PARCELA_COBRADA_VALOR = 'parcela_cobrada_valor'
    PARCELA_RECEBER_VALOR = 'parcela_receber_valor'
    PARCELA_VALOR = 'pedidoitem__cobrancas__cobranca__lancamento__valor'
    PARCELA_VENCIMENTO = 'pedidoitem__cobrancas__cobranca__lancamento__data'
    CORTESIA = 'pedidoitem__cortesia'
    DATA = 'pedidoitem__data_pedido'
    ENTREGA = 'entrega'
    NUMERO = 'numero'
    PAGAMENTO = \
        'pedidoitem__cobrancas__cobranca__lancamento__pagamentos__pagamento'
    PAGAMENTO_VALOR = (
        'pedidoitem__cobrancas__cobranca__'
        'lancamento__pagamentos__pagamento__valor'
    )
    PAGAMENTO_DATA = (
        'pedidoitem__cobrancas__cobranca__'
        'lancamento__pagamentos__pagamento__data'
    )
    PRECO = 'pedidoitem__preco'
    PROGRAMACAO = 'pedidoitem__programacao'
    QUANDO = 'pedidoitem__inserido_em'
    QUANTIDADE = 'pedidoitem__quantidade'
    USUARIO = 'pedidoitem__usuario__username'
    VALOR = 'valor'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Form_class = ListagemPedidoForm
        self.form_cookie_prefix = 'listagem_pedido'
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.cleaned_data2context = True
        self.template_name = 'bordado/listagem/pedido.html'
        self.title_name = "Pedido - Listagem"
        self.get_args = ['numero']
        self.get_vars2form = True

        self.form_report_excludes = []
        self.calculated_fields = [
            self.PARCELA_PEDIDO_VALOR,
            self.PARCELA_COBRADA_VALOR,
            self.PARCELA_RECEBER_VALOR,
        ]
        self.table_defs = TableDefsHBpSD(
            {
                self.NUMERO: ["Nº", 'c', 'c'],
                self.DATA: ["Data", 'c', 'c'],
                self.CLIENTE: ["Cliente", 'cp', 'l verde'],
                self.BORDADO_NOME: ["Bordado nome", 'cp', 'l amarelo'],
                self.BORDADO_CODIGO: ["Código", 'cp', 'l amarelo'],
                self.OBSERVACAO: ["Obs.", 'cp', 'l amarelo'],
                self.USUARIO: ["Usuário", 'c'],
                self.QUANDO: ["Quando", 'c'],
                self.ENTREGA: ["", 'cp', 'c azul'],
                self.QUANTIDADE: ["Quantidade", 'cp', 'r verde'],
                self.PRECO: ["Preço", 'cp', 'r verde'],
                self.PROGRAMACAO: ["Programação", 'cp', 'r verde'],
                self.AJUSTE: ["Ajuste", 'cp', 'r verde'],
                self.CORTESIA: ["Cortesia", 'cp', 'c azul'],
                self.VALOR: ["", 'cp', 'r azul'],
                self.COBRANCA: ["Cobrança", 'c', 'c'],
                self.COBRANCA_VALOR: ["Cobrança Valor", 'c', 'r'],
                self.COBRANCA_PEDIDO_VALOR: ["Cobrança Pedido Valor", 'c', 'r'],
                self.PARCELA_VALOR: ["Parcela Valor", 'c', 'r ouro'],
                self.PARCELA_PEDIDO_VALOR: [
                    "Parcela Pedido Valor", 'c', 'r ouro'],
                self.PARCELA_COBRADA_VALOR: [
                    "Parcela Pedido Cobrada Valor", 'c', 'r ouro'],
                self.PARCELA_RECEBER_VALOR: [
                    "Parcela Pedido Receber Valor", 'c', 'r ouro'],
                self.PARCELA_VENCIMENTO: [
                    "Parcela Vencimento", 'c', 'c ouro'],
                self.PAGAMENTO: ["Pagamento", 'c', 'c'],
                self.PAGAMENTO_VALOR: ["Valor", 'c', 'r'],
                self.PAGAMENTO_DATA: ["Data", 'c', 'c'],
            },
            style={
                'azul': "background-color: lightblue;",
                'verde': "background-color: lightgreen;",
                'amarelo': "background-color: khaki;",
                'ouro': "background-color: lightgoldenrodyellow;",
            },
        )

        self.mount_steps = [
            self.prepare_form_inputs,
            self.init_query,
            (self.get_filtro_cliente__apelido, 'filtro'),
            (self.get_filtro_icontains, 'filtro',
             [self.BORDADO_NOME, 'bordado_nome']),
            (self.get_filtro_icontains, 'filtro',
             [self.BORDADO_CODIGO, 'bordado_codigo']),
            (self.get_filtro_icontains, 'filtro',
             [self.OBSERVACAO, 'observacao']),
            (self.get_filtro_valor, 'filtro', ['numero']*2),
            (self.get_filtro_valor_de_ate, 'filtro',
             [self.DATA, 'data_de', 'data_ate']),
            (self.get_filtro_valor_de_ate, 'filtro',
             [self.ENTREGA, 'entrega_de', 'entrega_ate']),
            (self.get_filtro_valor_de_ate,  'filtro',
             [self.PARCELA_VENCIMENTO, 'cobranca_de', 'cobranca_ate']),
            self.get_filtro_fechamento,
            self.get_filtro_cortesia,
            self.get_filtro_cobranca,
            self.get_filtro_pagamento,
            self.order_query,
            self.annotate_query,
            self.exec_query,
            self.mount_pedidos_list,
            self.pre_prep_table,
            self.group_table,
            self.calcula_totalizador_geral,
            self.paginador,
            self.filtra_por_pedidos_pagina,            
            self.prep_table,
            self.calcula_totalizador_pagina,
            self.append_totalizador_geral,
            self.filter_report_excludes,
            self.context_table,
            self.form_report,
        ]

        self._today = datetime.date.today()
        self._max_por_pagina = 999_999

    def prepare_form_inputs(self):
        self.por_pagina = int(self.por_pagina)

    def init_query(self):
        self.query = Pedido.objects
        self.filtro = {}

    def get_filtro_fechamento(self):
        if self.fechamento == 'f':
            self.filtro[f'{self.ENTREGA}__isnull'] = False
        elif self.fechamento == 'n':
            self.filtro[f'{self.ENTREGA}__isnull'] = True

    def get_filtro_cortesia(self):
        if self.cortesia == 'f':
            self.filtro[self.CORTESIA] = True
        elif self.cortesia == 'n':
            self.filtro[self.CORTESIA] = False

    def get_filtro_cobranca(self):
        if self.cobranca == 'c':
            self.filtro[f'{self.COBRANCA}__isnull'] = False
        elif self.cobranca == 'n':
            self.filtro[f'{self.COBRANCA}__isnull'] = True

    def get_filtro_pagamento(self):
        if self.pagamento == 'p':
            self.filtro[f'{self.PAGAMENTO}__isnull'] = False
        elif self.pagamento == 'n':
            self.filtro[f'{self.PAGAMENTO}__isnull'] = True

    def order_query(self):
        if self.ordem == 'p':
            self.query = self.query.order_by(
                f'-{self.DATA}',
                '-numero',
                self.PARCELA_VENCIMENTO,
            )
        elif self.ordem == 'c':
            self.query = self.query.order_by(
                self.CLIENTE,
                f'-{self.ENTREGA}',
                f'-{self.DATA}',
                '-numero',
                self.PARCELA_VENCIMENTO,
            )
        else:
            self.query = self.query.order_by(
                f'-{self.ENTREGA}',
                self.CLIENTE,
                f'-{self.DATA}',
                '-numero',
                self.PARCELA_VENCIMENTO,
            )

    def annotate_query(self):
        self.query = self.query.annotate(
            valor=ExpressionWrapper(
                (F(self.QUANTIDADE) * F(self.PRECO))
                + F(self.PROGRAMACAO)
                + F(self.AJUSTE),
                output_field=DecimalField(decimal_places=2)
            )
        )
            
    def exec_query(self):
        self.data = self.query.filter(
            **self.filtro
        ).values(
            *(set(self.table_defs.all_fields) - set(self.calculated_fields)))
        if self.data:
            self.data = queryset2dictlist(self.data)
        else:
            raise StopStepsException(
                "Filtro definido não seleciona nenhum pedido")

    def mount_pedidos_list(self):
        self.pedidos_list = []
        for row in self.data:
            if row[self.NUMERO] not in self.pedidos_list:
                self.pedidos_list.append(row[self.NUMERO])

    def prep_parcela_pedido_valor(self, row):
        return self.prep_parcela_valor(row)

    def prep_parcela_cobrada_valor(self, row):
        return self.prep_parcela_valor(row, 'c')

    def prep_parcela_receber_valor(self, row):
        return self.prep_parcela_valor(row, 'r')

    def prep_parcela_valor(self, row, cobrada_receber=None):
        if cobrada_receber and row[self.PARCELA_VENCIMENTO]:
            if cobrada_receber == 'c':
                ok = row[self.PARCELA_VENCIMENTO] <= self._today
            else:
                ok = row[self.PARCELA_VENCIMENTO] > self._today
            if not ok:
                return Decimal('0.00')
        return decimal_proporcional(
            row[self.PARCELA_VALOR],
            row[self.COBRANCA_PEDIDO_VALOR],
            row[self.COBRANCA_VALOR],
        )

    def prep_parcela_pagamento_valor(self, row):
        return decimal_proporcional(
            row[self.PAGAMENTO_VALOR],
            row[self.COBRANCA_PEDIDO_VALOR],
            row[self.COBRANCA_VALOR],
        )

    def pre_prep_table(self):
        PrepRows(
            self.data,
        ).sub_sequence(
            'seq', self.NUMERO
        ).none(
            (
                'valor',
                self.COBRANCA_VALOR,
                self.PARCELA_VALOR,
                self.COBRANCA_PEDIDO_VALOR,
            ),
            Decimal('0.00')
        ).round(
            'valor', 2
        ).abs(
            self.PARCELA_VALOR,
        ).exec(
            self.PARCELA_PEDIDO_VALOR,
            self.prep_parcela_pedido_valor
        ).exec(
            self.PARCELA_COBRADA_VALOR,
            self.prep_parcela_cobrada_valor
        ).exec(
            self.PARCELA_RECEBER_VALOR,
            self.prep_parcela_receber_valor
        ).exec(
            self.PAGAMENTO_VALOR,
            self.prep_parcela_pagamento_valor
        ).process()

    def prep_table(self):
        PrepRows(
            self.data,
        ).str_dash(
            (
                self.BORDADO_CODIGO,
                self.COBRANCA,
                self.PAGAMENTO,
                self.OBSERVACAO,
            )
        ).date_dash(
            (
                self.ENTREGA,
                self.PARCELA_VENCIMENTO,
                self.PAGAMENTO_DATA,
            )
        ).sn(
            self.CORTESIA
        ).str(
            (
                self.BORDADO_NOME,
            ),
            '<Erro!>',
        ).process()

    def group_table(self):
        self.group = [
            self.NUMERO,
            self.DATA,
            self.CLIENTE,
            self.BORDADO_NOME,
            self.BORDADO_CODIGO,
            self.OBSERVACAO,
            self.USUARIO,
            self.QUANDO,
            self.ENTREGA,
            self.QUANTIDADE,
            self.PRECO,
            self.PROGRAMACAO,
            self.AJUSTE,
            self.CORTESIA,
            self.VALOR,
            self.COBRANCA,
            self.COBRANCA_VALOR,
            self.COBRANCA_PEDIDO_VALOR,
        ]
        group_rowspan(self.data, self.group)

    def calcula_totalizador(self, dados, descr):
        totalize_data(
            dados,
            {
                'sum': [
                    'valor',
                    self.COBRANCA_PEDIDO_VALOR,
                    self.PARCELA_PEDIDO_VALOR,
                    self.PARCELA_COBRADA_VALOR,
                    self.PARCELA_RECEBER_VALOR,
                ],
                'descr': {self.CLIENTE: descr},
                'row_if': {
                    'valor': {False: 'seq'},
                    self.COBRANCA_PEDIDO_VALOR: {False: 'seq'},
                },
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
            }
        )

    def calcula_totalizador_geral(self):
        self.calcula_totalizador(self.data, "Total geral:")
        self.total_geral = self.data.pop()

    def paginador(self):
        if self.por_pagina:
            por_pagina = self.por_pagina
            page = self.page
            pag_neib = 4
        else:
            por_pagina = self._max_por_pagina
            page = 1
            pag_neib = None
        self.pedidos_data, self.pedidos_pagina = list_paginator_basic(
            self.pedidos_list, por_pagina, page, pag_neib=pag_neib)

    def filtra_por_pedidos_pagina(self):
        self.data = [
            row
            for row in self.data
            if row[self.NUMERO] in self.pedidos_pagina
        ]

    def calcula_totalizador_pagina(self):
        if self.pedidos_data.paginator.num_pages > 1:
            self.calcula_totalizador(self.data, "Total da página:")

    def append_totalizador_geral(self):
        self.data.insert(0, self.total_geral)

    def filter_report_excludes(self):
        self.form_report_excludes.extend(['apresentacao', 'page'])

        for form_var in ['fechamento', 'cortesia', 'cobranca']:
            if getattr(self, form_var, '') == '':
                self.form_report_excludes.append(form_var)

        if (
            (not self.por_pagina) or
            (self.pedidos_data.paginator.num_pages == 1)
        ):
            self.form_report_excludes.append('por_pagina')
        
    def context_table(self):
        self.context['tabela']= {
            'data': self.data,
            'pedidos': self.pedidos_data,
            'group': self.group,
            'thclass': 'sticky',
        }
        self.table_defs.hfs_dict_context(
            self.context['tabela'],
            bitmap=self.apresentacao[0],
        )

    def form_report(self):
        self.context.update({
            'form_report': form_report(
                self.form,
                self.form_report_excludes,
            ),
        })
