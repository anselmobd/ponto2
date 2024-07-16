from pprint import pprint

from django.db import models
from django.utils import timezone

from o2lib.datetime.tz import tz_local

from bordado.models.cliente import Cliente
from bordado.models.dificuldade_bordado import DificuldadeBordado


__all__ = [
    'Bordado',
]


class BordadoManager(models.Manager):
    def get_by_natural_key(self, nome, codigo, cnpj9, cnpj4):
        return self.get(
            nome=nome, codigo=codigo, cliente__cnpj9=cnpj9, cliente__cnpj4=cnpj4)


class Bordado(models.Model):
    admin_order = 300
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    nome = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    codigo = models.CharField(
        "código",
        max_length=50,
        default="",
        blank=True,
        null=True,
    )
    pontos = models.PositiveIntegerField(
        default=0,
    )
    cores = models.PositiveIntegerField(
        default=0,
    )
    tamanho_maximo = models.PositiveIntegerField(
        "tamanho máximo",
        default=0,
        help_text="em milímetros",
    )
    dificuldade = models.ForeignKey(
        DificuldadeBordado,
        on_delete=models.PROTECT,
        default=DificuldadeBordado.id_indefinida,
    )

    objects = BordadoManager()

    def __str__(self):
        cliente = f" - {self.cliente}" if self.cliente else ""
        codigo = f" - {self.codigo}" if self.codigo else ""
        return f"{self.nome}{codigo}{cliente}"

    def save(self, *args, **kwargs):
        if not self.nome:
            self.nome = f"[{tz_local(timezone.now()):%H:%M:%S}]"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'po2_bordado'
        verbose_name = "Bordado"
        ordering = ['nome', 'codigo']
        unique_together = [['nome', 'codigo', 'cliente']]

    def natural_key(self):
        return (self.nome, self.codigo) + Cliente.nullable_natural_key(self.cliente)

    natural_key.dependencies = ['bordado.cliente']
