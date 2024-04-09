from rest_framework import serializers

from bordado.models import (
    Bordado,
)
from bordado.serializers.down.cliente import ClienteDownSerializer
from bordado.serializers.dificuldade_bordado import DificuldadeBordadoSerializer


__all__ = [
    'BordadoDownSerializer',
]


class BordadoDownSerializer(serializers.ModelSerializer):
    cliente = ClienteDownSerializer()
    dificuldade = DificuldadeBordadoSerializer()
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
