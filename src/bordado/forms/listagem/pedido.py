from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs


__all__ = [
    'ListagemPedidoForm',
]


class ListagemPedidoForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['cliente_apelido', 'numero'],
        ['bordado_nome', 'bordado_codigo', 'observacao'],
        # ['data_de', 'data_ate'],
        ['entrega_de', 'entrega_ate'],
        ['cobranca_de', 'cobranca_ate'],
        ['fechamento', 'cortesia', 'cobranca', 'pagamento'],
        ['ordem', 'apresentacao'],
        ['por_pagina', 'page']
    ]
    cookie_field = ['apresentacao', 'por_pagina']

    cliente_apelido = forms.CharField(
        label="Cliente",
        required=False,
        widget=forms.TextInput(
            attrs={**a.autofocus, **a.string}
        ),
    )
    numero = forms.CharField(
        label="Pedido nº",
        required=False,
        widget=forms.TextInput(
            attrs={**a.number, **a.placeholder_0, **a.size_6}
        ),
    )
    bordado_nome = forms.CharField(
        label="Bordado nome",
        required=False,
        widget=forms.TextInput(
            attrs={**a.string}
        ),
    )
    bordado_codigo = forms.CharField(
        label="Bordado código",
        required=False,
        widget=forms.TextInput(
            attrs={**a.string}
        ),
    )
    observacao = forms.CharField(
        label="Observação",
        required=False,
        widget=forms.TextInput(
            attrs={**a.string}
        ),
    )
    data_de = forms.DateField(
        label="Data de pedido: De",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    data_ate = forms.DateField(
        label="Até",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    entrega_de = forms.DateField(
        label="Data de entrega: De",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    entrega_ate = forms.DateField(
        label="Até",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    cobranca_de = forms.DateField(
        label="Data de cobrança: De",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    cobranca_ate = forms.DateField(
        label="Até",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    CHOICES = [
        ('', "Não filtra"),
        ('f', "Fechado"),
        ('n', "Não fechado"),
    ]
    fechamento = forms.ChoiceField(
        label="Fechamento",
        choices=CHOICES,
        initial='',
        required=False,
    )
    CHOICES = [
        ('', "Não filtra"),
        ('f', "Cortesia"),
        ('n', "Não Cortesia"),
    ]
    cortesia = forms.ChoiceField(
        label="Cortesia",
        choices=CHOICES,
        initial='',
        required=False,
    )
    CHOICES = [
        ('', "Não filtra"),
        ('c', "Cobrado"),
        ('n', "Não cobrado"),
    ]
    cobranca = forms.ChoiceField(
        label="Cobrança",
        choices=CHOICES,
        initial='',
        required=False,
    )
    CHOICES = [
        ('', "Não filtra"),
        ('p', "Pago"),
        ('n', "Não pago"),
    ]
    pagamento = forms.ChoiceField(
        label="Pagamento",
        choices=CHOICES,
        initial='',
        required=False,
    )
    CHOICES = [
        ('', "Data do pedido / Nº do pedido"),
        ('e', "Data de entrega / Cliente / Nº do pedido"),
    ]
    ordem = forms.ChoiceField(
        label="Ordem",
        choices=CHOICES,
        initial='',
        required=False,
    )
    CHOICES = [
        ('c', "Completa"),
        ('p', "Parcial"),
        # ('pc', "Parcial+Cores"),
    ]
    apresentacao = forms.ChoiceField(
        label="Apresentação",
        choices=CHOICES,
        initial='c',
        required=False,
    )
    por_pagina = forms.CharField(
        label="Pedidos por página",
        help_text="(Se zero, desliga paginação.)",
        required=True,
        initial='50',
        widget=forms.TextInput(
            attrs={**a.number, **a.placeholder_0, **a.size_6}
        ),
    )
    page = forms.IntegerField(
        label="Ir para página",
        required=True,
        initial='1',
        widget=forms.TextInput(
            attrs={**a.number, **a.placeholder_0, **a.size_6}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
