from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs


__all__ = [
    'CobrancaForm',
]


class CobrancaForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['numero', 'cliente_apelido'],
    ]

    numero = forms.CharField(
        label='Número',
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
