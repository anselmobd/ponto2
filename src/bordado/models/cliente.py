from pprint import pprint

from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.text import slugify

from o2lib.codes.cnpj import CNPJ
from o2lib.models.base import logged_user

from bordado.models.tipo_comunicacao import (
    TipoComunicacao,
    tipo_comunicacao_default_id,
)
from bordado.models.forma_pagamento import (
    FormaPagamento,
    forma_pagamento_default_id,
)


__all__ = [
    'Cliente',
]


class ClienteManager(models.Manager):
    def get_by_natural_key(self, cnpj9, cnpj4):
        return self.get(cnpj9=cnpj9, cnpj4=cnpj4)


class Cliente(models.Model):
    admin_order = 100
    # empresa = models.ForeignKey(
    #     Empresa,
    #     on_delete=models.PROTECT,
    # )
    nome = models.CharField(
        "Nome/Razão Social",
        max_length=100,
        blank=True,
    )
    fantasia = models.CharField(
        "Nome Fantasia",
        max_length=100,
        blank=True,
    )
    apelido = models.CharField(
        max_length=30,
        unique=True,
    )
    apelido_slug = models.SlugField(
        max_length=30,
        # unique=True,
        blank=True,
        null=True,
    )
    cnpj9 = models.PositiveIntegerField(
        "CNPJ (raiz)",
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(999_999_999)],
    )
    cnpj4 = models.PositiveSmallIntegerField(
        "CNPJ (filial)",
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(9_999)],
    )
    cnpj2 = models.PositiveSmallIntegerField(
        "CNPJ (dígitos)",
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(99)],
    )
    cep = models.CharField(
        "CEP",
        max_length=10,
        blank=True,
    )
    logradouro = models.CharField(
        max_length=100,
        blank=True,
    )
    numero = models.PositiveSmallIntegerField(
        "Número",
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(999_999)],
    )
    complemento = models.CharField(
        max_length=30,
        blank=True,
    )
    bairro = models.CharField(
        max_length=100,
        blank=True,
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
    )
    uf = models.CharField(
        max_length=2,
        blank=True,
    )
    comunicacao = models.ForeignKey(
        TipoComunicacao,
        default=tipo_comunicacao_default_id,
        on_delete=models.PROTECT,
        verbose_name="Comunicação preferêncial",
    )
    conta_corrente = models.BooleanField(
        "Financeiro tipo conta corrente?",
        default=False,
    )
    parcelamento = models.CharField(
        "Parcelamento padrão",
        max_length=30,
        default="",
        blank=True,
    )
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.PROTECT,
        verbose_name="Forma de pagamento",
        default=forma_pagamento_default_id,
    )
    nf = models.BooleanField(
        "Nota Fiscal por cobrança?",
        default=True,
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="usuário",
        default=logged_user,
    )
    quando = models.DateTimeField(auto_now=True)

    objects = ClienteManager()

    @property
    def cnpj(self):
        if ( self.cnpj9 is not None
            and self.cnpj4 is not None
            and self.cnpj2 is not None
        ):
            cnpj = CNPJ(self.cnpj9, self.cnpj4, self.cnpj2)
            mark = "" if cnpj.valid() else "!"
            return f"{cnpj}{mark}"
        else:
            return "!"

    def __str__(self):
        return self.apelido_slug

    def save(self, *args, **kwargs):
        self.apelido_slug = slugify(self.apelido)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'po2_cliente'
        verbose_name = "Cliente"
        ordering = ['apelido']
        # unique_together = [['cnpj9', 'cnpj4']]

    def natural_key(self):
        return (self.cnpj9, self.cnpj4)

    @staticmethod
    def nullable_natural_key(cliente):
        return (None, None) if cliente is None else cliente.natural_key()

    @staticmethod
    def default_client_id():
        return Cliente.objects.first().id
