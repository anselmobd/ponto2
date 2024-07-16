from pprint import pprint

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from bordado.models.pedido_item import PedidoItem


__all__ = [
    'OrdemProducao',
]


class OrdemProducao(models.Model):
    admin_order = 1000
    numero = models.AutoField(
        "Número",
        primary_key=True
    )
    pedido_item = models.ForeignKey(
        PedidoItem,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1_000_000)],
        default=0,
    )
    cancelado = models.BooleanField(
        default=False,
    )
    inserido_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OP {self.numero:04d}; {self.pedido_item}"

    class Meta:
        db_table = 'po2_op'
        verbose_name = "Ordem de produção"
        verbose_name_plural = "Ordens de produção"
        ordering = ['-numero']
