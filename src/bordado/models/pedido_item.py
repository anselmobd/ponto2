from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from o2lib.models.base import logged_user

from bordado.models.bordado import Bordado
from bordado.models.pedido import Pedido


__all__ = [
    'PedidoItem',
]


class PedidoItemManager(models.Manager):
    def get_by_natural_key(self, ordem, pedido):
        return self.get(ordem=ordem, pedido__numero=pedido)


class PedidoItem(models.Model):
    admin_order = 500
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    ordem = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=0,
    )
    data_pedido = models.DateField(
        "Data do pedido",
        default=timezone.localdate
    )
    inserido_em = models.DateTimeField(auto_now_add=True)
    bordado = models.ForeignKey(
        Bordado,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    observacao = models.CharField(
        "Observação",
        max_length=100,
        default="",
        blank=True,
        null=True,
    )
    quantidade = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(0.01)),
            MaxValueValidator(Decimal(1_000_000)),
        ],
        default=0,
    )
    preco = models.DecimalField(
        "Preço",
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(0.01)),
            MaxValueValidator(Decimal(1_000_000)),
        ],
        default=0,
    )
    programacao = models.DecimalField(
        "Pogramação",
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(0.01)),
            MaxValueValidator(Decimal(1_000_000)),
        ],
        default=0,
    )
    ajuste = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(-1_000)),
            MaxValueValidator(Decimal(1_000)),
        ],
        default=0,
    )
    cortesia = models.BooleanField(
        default=False,
    )
    cancelado = models.BooleanField(
        default=False,
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="usuário",
        default=logged_user,
    )

    objects = PedidoItemManager()

    @property
    def cliente(self):
        return self.pedido.cliente

    def __str__(self):
        return (
            f"{self.id}: {self.pedido.numero:04d}/{self.ordem} "
            f"{self.quantidade}*'{self.bordado}'"
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.ordem = (
                PedidoItem.objects.filter(pedido=self.pedido).count() + 1
            ) * 10
        super(PedidoItem, self).save(*args, **kwargs)

    class Meta:
        db_table = 'po2_pedido_item'
        verbose_name = "Item de pedido"
        verbose_name_plural = "Itens de pedido"
        ordering = ['-pedido__numero', '-ordem']
        unique_together = [['ordem', 'pedido']]

    def natural_key(self):
        return (self.ordem, self.pedido.numero)

    natural_key.dependencies = ['bordado.pedido']
