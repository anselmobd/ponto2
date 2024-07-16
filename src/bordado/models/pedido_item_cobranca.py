from decimal import Decimal
from pprint import pprint

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from bordado.models.cobranca import Cobranca
from bordado.models.pedido_item import PedidoItem


__all__ = [
    'PedidoItemCobranca',
]


class PedidoItemCobranca(models.Model):
    admin_order = 800
    pedido_item = models.ForeignKey(
        PedidoItem,
        on_delete=models.PROTECT,
        related_name='cobrancas',
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

    class Meta:
        db_table = 'po2_pedido_item_cobranca'
        verbose_name = "Cobrança de item de pedido"
        verbose_name_plural = "Cobranças de itens de pedido"
