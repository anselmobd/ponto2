from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs
from o2lib.date import ano_atual, mes_atual


__all__ = [
    'FinanceiroMesForm',
]


class FinanceiroMesForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['ano', 'mes'],
    ]

    ano = forms.IntegerField(
        label='Até ano',
        required=True,
        initial=ano_atual,
        widget=forms.TextInput(
            attrs={**a.autofocus, **a.number, **a.placeholder_0, **a.size_6}
        ),
    )

    mes = forms.IntegerField(
        label='Mês',
        required=True,
        initial=mes_atual,
        widget=forms.TextInput(
            attrs={**a.number, **a.placeholder_0, **a.size_6}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
