from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs
from o2lib.date import ano_atual, mes_atual


__all__ = [
    'AnaliseClienteForm',
]


class AnaliseClienteForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['apelido'],
    ]

    apelido = forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(
            attrs={**a.string, **a.autofocus}
        ),
        help_text="Se vazio ou selecionar mais de um cliente, lista clientes"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
