from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs


class LancamentoForm(forms.Form):
    a = FormWidgetAttrs()

    pedido_numero = forms.CharField(
        label='Pedido',
        required=False,
        widget=forms.TextInput(
            attrs={**a.autofocus, **a.number}
        ),
    )
    cobranca_id = forms.CharField(
        label='Cobrança',
        required=False,
        widget=forms.TextInput(
            attrs={**a.number}
        ),
    )
