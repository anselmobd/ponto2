from django.contrib.auth.models import User
from rest_framework import serializers

from bordado.models import (
    TipoComunicacao,
)


__all__ = [
    'TipoComunicacaoSerializer',
]


class TipoComunicacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoComunicacao
        fields = [
            'id',
            'descricao',
        ]
