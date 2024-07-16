from pprint import pprint

from django.db import models


__all__ = [
    'DificuldadeBordado',
]


class DificuldadeBordadoManager(models.Manager):
    def get_by_natural_key(self, ordem):
        return self.get(ordem=ordem)


class DificuldadeBordado(models.Model):
    admin_order = 200
    ordem = models.PositiveSmallIntegerField(
        unique=True,
    )
    descricao = models.CharField(
        "Descrição",
        max_length=50,
        unique=True,
    )

    objects = DificuldadeBordadoManager()

    def id_indefinida():
        return DificuldadeBordado.objects.get(ordem=0).id

    def __str__(self):
        return f"{self.ordem}-{self.descricao}"

    class Meta:
        db_table = 'po2_dificuldade_bordado'
        verbose_name = "Dificuldade de bordado"
        verbose_name_plural = "Dificuldades de bordado"
        ordering = ['ordem']

    def natural_key(self):
        return (self.ordem, )
