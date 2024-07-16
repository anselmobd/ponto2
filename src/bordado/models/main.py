from decimal import Decimal
from pprint import pprint

from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from o2lib.datetime.tz import tz_local
from o2lib.models.base import logged_user

from bordado.models.bordado import Bordado
from bordado.models.cliente import Cliente
from bordado.models.contato import Contato
from bordado.models.dificuldade_bordado import DificuldadeBordado
from bordado.models.forma_pagamento import (
    FormaPagamento,
    forma_pagamento_default_id,
)
from bordado.models.pedido import Pedido
from bordado.models.pedido_item import PedidoItem
from bordado.models.tipo_comunicacao import (
    TipoComunicacao,
    tipo_comunicacao_default_id,
)


__all__ = [
    'ApontamentoProducao',
    'Bordado',
    'Cliente',
    'Cobranca',
    'Contato',
    'DificuldadeBordado',
    'FormaPagamento',
    'forma_pagamento_default_id',
    'Lancamento',
    'logged_user',
    'OrdemProducao',
    'Pedido',
    'PedidoItem',
    'PedidoItemCobranca',
    'TipoComunicacao',
    'tipo_comunicacao_default_id',
]


# class Empresa(models.Model):
#     nome = models.CharField(
#         max_length=50,
#         unique=True,
#     )

#     def __str__(self):
#         return f"{self.nome}"

#     class Meta:
#         db_table = 'po2_empresa'
#         verbose_name = "Empresa"
#         ordering = ['nome']


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


class ApontamentoProducaoManager(models.Manager):
    def get_by_natural_key(self, apontado_em, op):
        return self.get(apontado_em=apontado_em, op__numero=op)


class ApontamentoProducao(models.Model):
    admin_order = 1100
    op = models.ForeignKey(
        OrdemProducao,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    qtd_perda = models.IntegerField(
        "quantidade de perda",
        validators=[MinValueValidator(0), MaxValueValidator(1_000_000)],
        default=0,
    )
    qtd_prod = models.IntegerField(
        "quantidade produzida",
        validators=[MinValueValidator(0), MaxValueValidator(1_000_000)],
        default=0,
    )
    apontado_em = models.DateTimeField(auto_now_add=True)
    encerrado = models.BooleanField(
        default=False,
    )

    objects = ApontamentoProducaoManager()

    def __str__(self):
        return (
            f"OP {self.op.numero:04d} {self.qtd_prod} ({self.qtd_perda}) "
            f"{tz_local(self.apontado_em):%d/%m/%Y %H:%M:%S}"
        )
    class Meta:
        db_table = 'po2_aponta_prod'
        verbose_name = "Apontamento de produção"
        verbose_name_plural = "Apontamentos de produção"
        ordering = ['-op_id', 'apontado_em']
        unique_together = [['apontado_em', 'op']]

    def natural_key(self):
        return (self.apontado_em, self.op.numero)

    natural_key.dependencies = ['bordado.ordemproducao']
