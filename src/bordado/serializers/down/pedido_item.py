from rest_framework import serializers

from bordado.models import (
    PedidoItem,
)
from bordado.serializers.down.bordado import BordadoDownSerializer
from bordado.serializers.down.pedido import PedidoDownSerializer
from bordado.serializers.simple.user import UserSimpleSerializer


__all__ = [
    'PedidoItemDownSerializer',
]


class PedidoItemDownSerializer(serializers.ModelSerializer):
    pedido = PedidoDownSerializer()
    bordado = BordadoDownSerializer()
    usuario = UserSimpleSerializer()

    class Meta:
        model = PedidoItem
        fields = [
            'id',
            'pedido',
            'ordem',
            'data',
            'inserido_em',
            'bordado',
            'quantidade',
            'preco',
            'programacao',
            'ajuste',
            'cancelado',
            'usuario',
            # 'ordemproducao'  # Não utilizado por ora
        ]
