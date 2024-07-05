from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs


__all__ = [
    'CobrancaForm',
]


class CobrancaForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['cliente_apelido', 'numero'],
        ['data_de', 'data_ate'],
    ]

    numero = forms.CharField(
        label='Cobrança nº',
        required=False,
        widget=forms.TextInput(
            attrs={**a.autofocus, **a.number, **a.placeholder_0, **a.size_6}
        ),
    )
    cliente_apelido = forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(
            attrs={**a.string}
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
