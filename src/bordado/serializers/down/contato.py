from rest_framework import serializers

from bordado.models import (
    Cliente,
    Contato,
)
from bordado.serializers.down.cliente import ClienteDownSerializer


__all__ = [
    'ContatoDownSerializer',
]


class ContatoDownSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())

    class Meta:
        model = Contato
        fields = [
            'id',
            'cliente',
            'nome',
            'telefone',
            'email',
            'preferencial',
        ]
