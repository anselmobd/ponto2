from rest_framework import serializers

from bordado.models import (
    Bordado,
)


__all__ = [
    'BordadoSimpleSerializer',
]


class BordadoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bordado
        fields = [
            'id',
            'cliente',
            'nome',
            'codigo',
            'pontos',
            'cores',
            'tamanho_maximo',
            'dificuldade',
        ]
