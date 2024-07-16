from pprint import pprint

from django.db import models


__all__ = [
    'FormaPagamento',
    'forma_pagamento_default_id',
]


class FormaPagamento(models.Model):
    admin_order = 75
    nome = models.CharField(
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'po2_forma_pagamento'
        verbose_name = "Forma de pagamento"
        verbose_name_plural = "Formas de pagamento"
        ordering = ['id']


def forma_pagamento_default_id():
    forma_pagamento = FormaPagamento.objects.filter(nome="Boleto").first()
    if forma_pagamento:
        return forma_pagamento.id
    return None
