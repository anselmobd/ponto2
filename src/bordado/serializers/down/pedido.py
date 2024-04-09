from rest_framework import serializers

from bordado.models import (
    Pedido,
)
from bordado.serializers.down.cliente import ClienteDownSerializer


__all__ = [
    'PedidoDownSerializer',
]


class PedidoDownSerializer(serializers.ModelSerializer):
    cliente = ClienteDownSerializer()
    class Meta:
        model = Pedido
        fields = [
            'numero',
            'cliente',
            'inserido_em',
            'entrega',
            'cancelado',
        ]
