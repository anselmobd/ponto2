from decimal import Decimal
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F

from o2lib.form.form_report import form_report
from o2lib.models.row_field import PrepRows
from o2lib.models.dictlist import queryset2dictlist
from o2lib.table_defs import TableDefsHBpSD
from o2lib.views.base.get_post import O2BaseGetPostView
from o2lib.views.base.exception import StopStepsException
from o2lib.views.totalize import totalize_data
from o2lib.views.paginator import paginator_basic

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
    CORTESIA = 'pedidoitem__cortesia'
    DATA = 'pedidoitem__data_pedido'
    ENTREGA = 'entrega'
    NUMERO = 'numero'
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
            },
            style={
                'azul': "background-color: lightblue;",
                'verde': "background-color: lightgreen;",
                'amarelo': "background-color: khaki;",
            },
        )

        self.mount_steps = [
            self.init_query,
            self.filtra_cliente__apelido,
            (self.filtra_valor, ['numero']*2),
            (self.filtra_valor_de_ate, [self.DATA, 'data_de', 'data_ate']),
            (self.filtra_valor_de_ate, [
                self.ENTREGA, 'entrega_de', 'entrega_ate']),
            self.filtra_fechamento,
            self.filtra_cortesia,
            self.filtra_cobranca,
            self.order_query,
            self.annotate_query,
            self.exec_query,
            self.pre_prep_table,
            self.calcula_totalizador_geral,
            self.paginador,
            self.prep_table,
            self.calcula_totalizador_pagina,
            self.append_totalizador_geral,
            self.filter_report_excludes,
            self.context_table,
            self.form_report,
        ]

    def init_query(self):
        self.query = Pedido.objects

    def filtra_fechamento(self):
        if self.fechamento == 'f':
            self.query = self.query.filter(entrega__isnull=False)
        elif self.fechamento == 'n':
            self.query = self.query.filter(entrega__isnull=True)

    def filtra_cortesia(self):
        if self.cortesia == 'f':
            self.query = self.query.filter(**{self.CORTESIA: True})
        elif self.cortesia == 'n':
            self.query = self.query.filter(**{self.CORTESIA: False})

    def filtra_cobranca(self):
        if self.cobranca == 'c':
            self.query = self.query.filter(
                pedidoitem__cobrancas__cobranca__isnull=False)
        elif self.cobranca == 'n':
            self.query = self.query.filter(
                pedidoitem__cobrancas__cobranca__isnull=True)

    def order_query(self):
        if self.ordem == 'e':
            self.query = self.query.order_by(
                f'-{self.ENTREGA}', self.CLIENTE, '-numero'
            )
        else:
            self.query = self.query.order_by(
                f'-{self.DATA}', '-numero'
            )

    def annotate_query(self):
        self.query = self.query.annotate(
            valor=(
                F(self.QUANTIDADE) * F(self.PRECO) +
                F(self.PROGRAMACAO) +
                F(self.AJUSTE)
            )
        )
            
    def exec_query(self):
        self.data = self.query.values(
            *self.table_defs.all_fields)
        if self.data:
            self.data = queryset2dictlist(self.data)
        else:
            raise StopStepsException(
                "Filtro definido não seleciona nenhum pedido")

    def pre_prep_table(self):
        PrepRows(
            self.data,
        ).none(
            'valor', Decimal('0.00')
        ).round(
            'valor', 2
        ).process()

    def prep_table(self):
        PrepRows(
            self.data.object_list,
        ).str_dash(
            (
                self.BORDADO_CODIGO,
                self.COBRANCA,
                self.OBSERVACAO,
            )
        ).date_dash(
            (
                self.ENTREGA,
            )
        ).sn(
            self.CORTESIA
        ).str(
            (
                self.BORDADO_NOME,
            ),
            '<Erro!>',
        ).process()

    def calcula_totalizador(self, dados, descr):
        totalize_data(
            dados,
            {
                'sum': ['valor'],
                'descr': {self.CLIENTE: descr},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
            }
        )

    def calcula_totalizador_geral(self):
        self.calcula_totalizador(self.data, "Total geral:")
        self.total_geral = self.data.pop()

    def paginador(self):
        self.por_pagina = int(self.por_pagina)
        if not self.por_pagina:
            self.data = paginator_basic(
                self.data, 999_999, 1)
        else:
            self.data = paginator_basic(
                self.data, self.por_pagina, self.page, pag_neib=4)
        self.form.data['page'] = self.data.number

    def calcula_totalizador_pagina(self):
        if self.data.paginator.num_pages > 1:
            self.calcula_totalizador(self.data.object_list, "Total da página:")

    def append_totalizador_geral(self):
        self.data.object_list.insert(0, self.total_geral)

    def filter_report_excludes(self):
        if self.fechamento == '':
            self.form_report_excludes.append('fechamento')
        if self.cortesia == '':
            self.form_report_excludes.append('cortesia')
        if self.cobranca == '':
            self.form_report_excludes.append('cobranca')
        self.form_report_excludes.append('apresentacao')
        if (not self.por_pagina) or (self.data.paginator.num_pages == 1):
            self.form_report_excludes.append('por_pagina')
        self.form_report_excludes.append('page')

    def context_table(self):
        self.context['tabela']= {
            'data': self.data,
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
