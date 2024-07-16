from decimal import Decimal
from pprint import pprint

from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from o2lib.models.base import logged_user

from bordado.models.cliente import Cliente
from bordado.models.tipo_comunicacao import TipoComunicacao


__all__ = [
    'Cobranca',
]


class Cobranca(models.Model):
    admin_order = 700
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
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
    informacao = models.CharField(
        max_length=50,
        default="",
        blank=True,
        null=True,
    )
    comunicacao = models.ForeignKey(
        TipoComunicacao,
        on_delete=models.PROTECT,
    )
    nf = models.PositiveIntegerField(
        "NF",
        blank=True,
        null=True,
    )
    data = models.DateField(
    )
    parcelamento = models.CharField(
        max_length=50,
        default="0",
        blank=True,
        null=True,
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="usuário",
        default=logged_user,
    )
    quando = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        nf = f" - NF {self.nf}" if self.nf else ""
        return f"{self.id} - {self.data}{nf}"

    class Meta:
        db_table = 'po2_cobranca'
        verbose_name = "Cobrança"
        ordering = ['-id']
