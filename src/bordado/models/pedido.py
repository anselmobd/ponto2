from pprint import pprint

from django.db import models


__all__ = [
    'Pedido',
]


class Pedido(models.Model):
    admin_order = 400
    numero = models.AutoField(
        "Número",
        primary_key=True
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    inserido_em = models.DateTimeField(auto_now_add=True)
    entrega = models.DateField(
        blank=True,
        null=True,
    )
    cancelado = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"{self.numero:04d} - {self.cliente}"

    class Meta:
        db_table = 'po2_pedido'
        ordering = ['-numero']
