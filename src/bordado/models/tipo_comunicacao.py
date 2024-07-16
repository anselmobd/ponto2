from pprint import pprint

from django.db import models


__all__ = [
    'TipoComunicacao',
    'tipo_comunicacao_default_id',
]


class TipoComunicacao(models.Model):
    admin_order = 50
    descricao = models.CharField(
        "Descrição",
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = 'po2_tipo_comunicacao'
        verbose_name = "Tipo de comunicação"
        verbose_name_plural = "Tipos de comunicação"
        ordering = ['id']


def tipo_comunicacao_default_id():
    tipo_comunicacao = TipoComunicacao.objects.filter(descricao="Telefone").first()
    if tipo_comunicacao:
        return tipo_comunicacao.id
    return None
