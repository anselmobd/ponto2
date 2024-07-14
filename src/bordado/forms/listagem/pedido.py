from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs


__all__ = [
    'PedidoForm',
]


class PedidoForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['cliente_apelido', 'numero'],
        ['data_de', 'data_ate'],
        ['entrega_de', 'entrega_ate'],
    ]

    cliente_apelido = forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(
            attrs={**a.autofocus, **a.string}
        ),
    )
    numero = forms.CharField(
        label='Pedido nº',
        required=False,
        widget=forms.TextInput(
            attrs={**a.number, **a.placeholder_0, **a.size_6}
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
