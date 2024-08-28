from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs


__all__ = [
    'ListagemLancamentoForm',
]


class ListagemLancamentoForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['cliente_apelido', 'pedido_numero', 'cobranca_id'],
        ['data_de', 'data_ate'],
        ['tipo_lancamento', 'ordem'],
    ]

    cliente_apelido = forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(
            attrs={**a.autofocus, **a.string}
        ),
    )
    pedido_numero = forms.CharField(
        label='Pedido nº',
        required=False,
        widget=forms.TextInput(
            attrs={**a.number, **a.placeholder_0, **a.size_5}
        ),
    )
    cobranca_id = forms.CharField(
        label='Cobrança nº',
        required=False,
        widget=forms.TextInput(
            attrs={**a.number, **a.placeholder_0, **a.size_5}
        ),
    )
    data_de = forms.DateField(
        label="Data do lançamento: De",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    data_ate = forms.DateField(
        label="Até",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    CHOICES = [
        ('-', 'Não filtra'),
        ('c', 'Cobranças'),
        ('r', 'Recebimentos'),
    ]
    tipo_lancamento = forms.ChoiceField(
        label='Tipo de lançamento',
        choices=CHOICES,
        initial='-',
    )
    CHOICES = [
        ('p', 'Padrão'),
        ('c', 'Cliente'),
    ]
    ordem = forms.ChoiceField(
        label='Ordenação',
        choices=CHOICES,
        initial='p',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
