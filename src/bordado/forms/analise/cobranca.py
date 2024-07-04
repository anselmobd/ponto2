from pprint import pprint

from django import forms

from o2lib.form.widget_attrs import FormWidgetAttrs
from o2lib.date import ano_atual, mes_atual


__all__ = [
    'AnaliseCobrancaForm',
]


class AnaliseCobrancaForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['ano', 'mes'],
        ['cliente_apelido'],
        ['totaliza', 'ordem'],
    ]

    ano = forms.IntegerField(
        required=False,
        initial=ano_atual,
        widget=forms.NumberInput(),
    )

    mes = forms.IntegerField(
        required=False,
        initial=mes_atual,
    )

    cliente_apelido = forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(
            attrs={**a.string, **a.autofocus}
        ),
    )

    CHOICES = [
        ('c', 'Por cliente'),
        ('a', 'Por ano'),
        ('m', 'Por mês'),
    ]
    totaliza = forms.ChoiceField(
        choices=CHOICES,
        initial='c',
    )

    CHOICES = [
        ('i', 'Pela informação totalizada'),
        ('v', 'Pelo valor descrescente'),
    ]
    ordem = forms.ChoiceField(
        choices=CHOICES,
        initial='v',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
