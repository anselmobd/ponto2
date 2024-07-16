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
from bordado.models.cobranca import Cobranca


__all__ = [
    'Lancamento',
]


class Lancamento(models.Model):
    admin_order = 900
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
    )
    data = models.DateField(
    )
    cobranca = models.ForeignKey(
        Cobranca,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    parcela = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    n_parcelas = models.PositiveSmallIntegerField(
        "Nº de parcelas",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    informacao = models.CharField(
        "Informação",
        max_length=50,
    )
    valor = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(-1_000_000)),
            MaxValueValidator(Decimal(1_000_000)),
        ],
        default=0,
    )
    calculando = models.BooleanField(
        default=False,
    )
    saldo_cliente = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(-1_000_000)),
            MaxValueValidator(Decimal(1_000_000)),
        ],
        default=0,
    )
    saldo_empresa = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(-1_000_000)),
            MaxValueValidator(Decimal(1_000_000)),
        ],
        default=0,
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="usuário",
        related_name='+',
        default=logged_user,
    )
    quando = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}: {self.data} {self.cliente}"

    class Meta:
        db_table = 'po2_lancamento'
        verbose_name = "Lançamento"
        ordering = ['-data', '-id']
