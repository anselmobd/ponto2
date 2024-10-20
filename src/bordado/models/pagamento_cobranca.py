from decimal import Decimal

import django.utils.timezone
from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from o2lib.models.base import first_user_id, logged_user

from bordado.models.lancamento import Lancamento
from bordado.models.cobranca import Cobranca


__all__ = [
    'PagamentoCobranca',
]


class PagamentoCobranca(models.Model):
    admin_order = 950
    pagamento = models.ForeignKey(
        Lancamento,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    cobranca = models.ForeignKey(
        Cobranca,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    valor = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(0.01)),
            MaxValueValidator(Decimal(1_000_000)),
        ],
        default=0,
    )
    inserido_em = models.DateTimeField(auto_now_add=True)
    inserido_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        default=logged_user,
    )
    alterado_em = models.DateTimeField(
        default=django.utils.timezone.now
    )
    alterado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        default=first_user_id,
    )

    def __str__(self):
        return (
            f"Pag.({self.pagamento}) Cobr.({self.cobranca}) {self.valor}"
        )

    class Meta:
        db_table = 'po2_pagamento_cobranca'
        verbose_name = "Pagamento-Cobrança"
        verbose_name_plural = "Pagamentos-Cobranças"
