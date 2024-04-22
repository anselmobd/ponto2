from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs

__all__ = ['LancamentoForm']


class LancamentoForm(forms.Form):
    a = FormWidgetAttrs()

    cliente_apelido = forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(
            attrs={**a.autofocus, **a.string}
        ),
    )
    pedido_numero = forms.CharField(
        label='Pedido',
        required=False,
        widget=forms.TextInput(
            attrs={**a.number, **a.placeholder_0, **a.size_5}
        ),
    )
    cobranca_id = forms.CharField(
        label='Cobrança',
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
