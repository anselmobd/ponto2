from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs


__all__ = [
    'FaturamentoForm',
]


class FaturamentoForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['cliente_apelido', 'nf'],
        ['data_de', 'data_ate'],
    ]

    cliente_apelido = forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(
            attrs={**a.autofocus, **a.string}
        ),
    )
    nf = forms.CharField(
        label='NF',
        required=False,
        widget=forms.TextInput(
            attrs={**a.number, **a.placeholder_0, **a.size_6}
        ),
    )
    data_de = forms.DateField(
        label="Data da cobrança: De",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    data_ate = forms.DateField(
        label="Até",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
