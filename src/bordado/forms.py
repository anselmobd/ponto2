from pprint import pprint

from django import forms


class FinanceiroForm(forms.Form):
    pedido_numero = forms.CharField(
        label='Pedido',
        widget=forms.TextInput(
            attrs={
                'type': 'number',
                'autofocus': 'autofocus',
            }
        ),
        required=False,
    )
    cobranca_id = forms.CharField(
        label='Cobrança',
        widget=forms.TextInput(
            attrs={
                'type': 'number',
            }
        ),
        required=False,
    )
