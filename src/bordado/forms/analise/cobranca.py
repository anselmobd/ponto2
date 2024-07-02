from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs

__all__ = [
    'AnaliseCobrancaForm',
]


class AnaliseCobrancaForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['cliente_apelido'],
    ]

    cliente_apelido = forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(
            attrs={**a.string}
        ),
    )
