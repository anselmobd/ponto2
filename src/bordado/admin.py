from ponto2.admin import admin

from .models import (
    ApontamentoProducao,
    Bordado,
    Cliente,
    Cobranca,
    DificuldadeBordado,
    Lancamento,
    OrdemProducao,
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
    list_display = ['__str__', 'usuario', 'quando']
    search_fields = ['__str__']
    fields = [
        'apelido',
        (
            'nome',
            'fansasia',
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
        # 'boleto',
        # 'conta_corrente',
        # 'parcela',
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
        # 'parcela': 'width: 3em;',
    }
    readonly_fields = [
        'usuario',
        'quando',
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
        'nome', 'codigo', 'cliente', 'pontos', 'cores', 'tamanho_maximo', 'dificuldade'
    ]
    list_display_links = ['cliente', 'nome', 'codigo']
    search_fields = ['cliente__apelido', 'cliente__cnpj9', 'nome', 'codigo']
    list_filter = ['cliente']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'cliente',
        'inserido_em',
        'entrega',
        'cancelado',
    ]
    list_display_links = ['cliente', '__str__']
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
        'ordem',
        'pedido',
        'inserido_em',
        'bordado',
        'quantidade',
        'preco',
        'cancelado',
    ]
    list_display_links = [
        'ordem',
        'pedido',
    ]
    list_filter = [
        'pedido__cliente',
        'pedido',
    ]
    fields = [
        'pedido',
        'ordem',
        'usuario',
        'inserido_em',
        'bordado',
        'quantidade',
        'preco',
        'programacao',
        'ajuste',
        'cancelado',
    ]
    readonly_fields = [
        'ordem',
        'usuario',
        'inserido_em',
    ]


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


@admin.register(PedidoItemCobranca)
class PedidoItemCobrancaAdmin(admin.ModelAdmin):
    list_display = [
        'pedido_item',
        'cobranca',
        'valor',
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
