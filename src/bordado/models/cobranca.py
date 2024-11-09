from decimal import Decimal
from pprint import pprint

from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from o2lib.models.base import logged_user
from o2lib.strings import join_non_empty

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
 
    def id_str(self):
        return f"{self.id}"
 
    def nf_str(self):
        return f"NF {self.nf}" if self.nf else ""
 
    def data_str(self):
        return f"{self.data:%d/%m/%Y}"

    def __str__(self):
        return join_non_empty(
            " ", [self.id_str(), self.data_str(), self.nf_str()])
    
    class Meta:
        db_table = 'po2_cobranca'
        verbose_name = "Cobrança"
        ordering = ['-id']
