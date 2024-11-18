from pprint import pprint

from ponto2.admin import admin

from .models import (
    ApontamentoProducao,
    Bordado,
    Cliente,
    Cobranca,
    Contato,
    DificuldadeBordado,
    FormaPagamento,
    Lancamento,
    OrdemProducao,
    PagamentoCobranca,
    Pedido,
    PedidoItem,
    PedidoItemCobranca,
    TipoComunicacao,
)


class CustomModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(CustomModelAdmin, self).get_form(request, obj, **kwargs)
        if hasattr(self, 'field_style'):
            for field, style in self.field_style.items():
                form.base_fields[field].widget.attrs['style'] = style
        return form

# @admin.register(Empresa)
# class EmpresaAdmin(admin.ModelAdmin):
#     search_fields = ['nome']


@admin.register(Cliente)
class ClienteAdmin(CustomModelAdmin):
    list_display = ['apelido_slug', 'apelido', 'cnpj', 'usuario', 'quando']
    search_fields = ['apelido_slug', 'apelido', 'cnpj']
    fields = [
        (
            'apelido',
            'apelido_slug',
        ),
        (
            'nome',
            'fantasia',
        ),
        (
            'cnpj9',
            'cnpj4',
            'cnpj2',
        ),
        'cep',
        (
            'bairro',
            'cidade',
            'uf',
        ),
        (
            'logradouro',
            'numero',
            'complemento',
        ),
        (
            'comunicacao',
            'parcelamento',
            'nf',
        ),
        (
            'forma_pagamento',
            'conta_corrente',
        ),
        (
            'usuario',
            'quando',
        ),
    ]
    field_style = {
        'cnpj9': 'width: 9em;',
        'cnpj4': 'width: 4em;',
        'cnpj2': 'width: 3em;',
        'cep': 'width: 10em;',
        'complemento': 'width: 10em;',
        'uf': 'width: 3em;',
    }
    readonly_fields = [
        'apelido_slug',
        'usuario',
        'quando',
    ]
    list_filter = ['usuario', 'quando']


@admin.register(Contato)
class ContatoAdmin(CustomModelAdmin):
    list_display = [
        'id',
        'cliente',
        'nome',
        'telefone',
        'email',
        'preferencial',
    ]
    list_display_links = [
        'id',
        'cliente',
        'nome',
    ]
    search_fields = [
        'cliente',
        'nome',
        'telefone',
        'email',
    ]
    fields = list_display
    readonly_fields = [
        'id',
    ]


@admin.register(DificuldadeBordado)
class DificuldadeBordadoAdmin(CustomModelAdmin):
    list_display = ['__str__']
    search_fields = ['__str__']
    field_style = {
        'ordem': 'width: 3em;',
    }


@admin.register(Bordado)
class BordadoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'cliente', 'nome', 'codigo', 'pontos', 'cores', 'tamanho_maximo', 'dificuldade'
    ]
    list_display_links = ['id', 'cliente', 'nome', 'codigo']
    search_fields = ['id', 'cliente__apelido_slug', 'nome', 'codigo']
    list_filter = ['cliente']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'numero',
        'cliente',
        'inserido_em',
        'entrega',
        'cancelado',
    ]
    list_display_links = [
        'numero',
        'cliente',
    ]
    list_filter = [
        'cliente',
    ]
    fields = [
        'numero',
        'inserido_em',
        'cliente',
        'entrega',
        'cancelado',
    ]
    readonly_fields = [
        'numero',
        'inserido_em',
    ]


@admin.register(PedidoItem)
class PedidoItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'data_pedido',
        'pedido',
        'ordem',
        'inserido_em',
        'bordado',
        'observacao',
        'quantidade',
        'preco',
        'cortesia',
        'cancelado',
    ]
    list_display_links = [
        'id',
        'data_pedido',
        'pedido',
        'ordem',
    ]
    list_filter = [
        'pedido__cliente',
        'pedido',
    ]
    fields = [
        'id',
        'data_pedido',
        'pedido',
        'ordem',
        'usuario',
        'inserido_em',
        'bordado',
        'observacao',
        'quantidade',
        'preco',
        'programacao',
        'ajuste',
        'cortesia',
        'cancelado',
    ]
    readonly_fields = [
        'id',
        'ordem',
        'usuario',
        'inserido_em',
    ]


class CobrancaDataAnoFilter(admin.SimpleListFilter):
    title = 'Data / Ano'
    parameter_name = 'cobranca_data_ano_filter'

    def lookups(self, request, model_admin):
        dados = Cobranca.objects.all().values('data__year')
        anos = list(
            set(
                (row['data__year'], row['data__year'])
                for row in dados
            )
        )
        return anos

    def queryset(self, request, queryset):
        if self.value():
            self.title = f'Data / Ano = {self.value()}'
            return queryset.filter(data__year=self.value())
        else:
            self.title = 'Data / Ano'


class DataMesFilter(admin.SimpleListFilter):
    title = 'Data / Mês'
    parameter_name = 'data_mes_filter'

    _meses = {
        '1': '01-Janeiro',
        '2': '02-Fevereiro',
        '3': '03-Março',
        '4': '04-Abril',
        '5': '05-Maio',
        '6': '06-Junho',
        '7': '07-Julho',
        '8': '08-Agosto',
        '9': '09-Setembro',
        '10': '10-Outubro',
        '11': '11-Novembro',
        '12': '12-Dezembro',
    }

    def lookups(self, request, model_admin):
        return self._meses.items()

    def queryset(self, request, queryset):
        if self.value():
            self.title = f'Data / Mês = {self._meses[self.value()]}'
            return queryset.filter(data__month=self.value())
        else:
            self.title = 'Data / Mês'


@admin.register(Cobranca)
class CobrancaAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'cliente',
        'informacao',
        'comunicacao',
        'nf',
        'valor',
        'data',
        'parcelamento',
        'usuario',
        'quando',
    ]
    readonly_fields = [
        'usuario',
        'quando',
    ]
    search_fields = [
        'id',
        'cliente__apelido_slug',
        'informacao',
        'comunicacao__descricao',
        'nf',
        'valor',
    ]
    list_filter = [
        CobrancaDataAnoFilter,
        DataMesFilter,
        'usuario',
        'comunicacao',
        'cliente',
    ]


@admin.register(PedidoItemCobranca)
class PedidoItemCobrancaAdmin(admin.ModelAdmin):
    list_display = [
        'pedido_item',
        'cobranca',
        'valor',
    ]
    search_fields = [
        'pedido_item__id',
        'cobranca__id',
        'valor',
    ]
    list_filter = [
        'cobranca__cliente',
    ]


@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'cobranca',
        'parcela',
        'n_parcelas',
        'informacao',
        'valor',
        'saldo_cliente',
        'saldo_empresa',
        'usuario',
        'quando',
    ]
    list_filter = [
        'cliente',
    ]
    readonly_fields = [
        'calculando',
        'saldo_cliente',
        'saldo_empresa',
        'usuario',
        'quando',
    ]


@admin.register(OrdemProducao)
class OrdemProducaoAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'quantidade',
        'cancelado',
        'inserido_em',
    ]
    fields = [
        'numero',
        'inserido_em',
        'pedido_item',
        'quantidade',
        'cancelado',
    ]
    readonly_fields = [
        'numero',
        'inserido_em',
    ]


@admin.register(ApontamentoProducao)
class ApontamentoProducaoAdmin(admin.ModelAdmin):
    list_display = [
        'op',
        'qtd_prod',
        'qtd_perda',
        'encerrado',
        'apontado_em',
    ]
    fields = [
        'op',
        'qtd_prod',
        'qtd_perda',
        'encerrado',
        'apontado_em',
    ]
    readonly_fields = [
        'apontado_em',
    ]


@admin.register(TipoComunicacao)
class TipoComunicacaoAdmin(CustomModelAdmin):
    list_display = ['__str__']
    search_fields = ['__str__']
    fields = [
        'id',
        'descricao',
    ]
    readonly_fields = [
        'id',
    ]


@admin.register(FormaPagamento)
class FormaPagamentoAdmin(CustomModelAdmin):
    list_display = ['__str__']
    search_fields = ['__str__']
    fields = [
        'id',
        'nome',
    ]
    readonly_fields = [
        'id',
    ]

@admin.register(PagamentoCobranca)
class PagamentoCobrancaAdmin(CustomModelAdmin):
    readonly_fields = [
        'inserido_em',
        'inserido_por',
        'alterado_em',
        'alterado_por',
    ]
