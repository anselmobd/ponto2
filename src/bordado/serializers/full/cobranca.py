from rest_framework import serializers

from bordado.models import (
    Cobranca,
    Lancamento,
    PedidoItem,
    PedidoItemCobranca,
)
from bordado.serializers.down.bordado import BordadoDownSerializer
from bordado.serializers.down.cliente import ClienteDownSerializer
from bordado.serializers.down.pedido import PedidoDownSerializer
from bordado.serializers.simple.tipo_comunicacao import TipoComunicacaoSimpleSerializer
from bordado.serializers.simple.user import UserSimpleSerializer


class PedidoItemSerializer(serializers.ModelSerializer):
    pedido = PedidoDownSerializer()
    bordado = BordadoDownSerializer()
    usuario = UserSimpleSerializer()

    class Meta:
        model = PedidoItem
        fields = [
            'id',
            'pedido',
            'ordem',
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


class PedidoItemCobrancasSerializer(serializers.ModelSerializer):
    pedido_item = PedidoItemSerializer()

    class Meta:
        model = PedidoItemCobranca
        fields = [
            'id',
            'pedido_item',
            'valor',
        ]


class LancamentoSerializer(serializers.ModelSerializer):
    cliente = ClienteDownSerializer()
    usuario = UserSimpleSerializer()

    class Meta:
        model = Lancamento
        fields = [
            'id',
            'cliente',
            'data',
            'parcela',
            'n_parcelas',
            'informacao',
            'valor',
            'calculando',
            'saldo_cliente',
            'saldo_empresa',
            'usuario',
            'quando',
        ]


class CobrancaSerializer(serializers.ModelSerializer):
    cliente = ClienteDownSerializer()
    comunicacao = TipoComunicacaoSimpleSerializer()
    usuario = UserSimpleSerializer()
    pedidoitemcobranca_set = PedidoItemCobrancasSerializer(many=True, read_only=True)
    lancamento_set = LancamentoSerializer(many=True, read_only=True)

    class Meta:
        model = Cobranca
        fields = [
            'id',
            'cliente',
            'valor',
            'tipo',
            'comunicacao',
            'nf',
            'data',
            'parcelamento',
            'usuario',
            'quando',
            'pedidoitemcobranca_set',
            'lancamento_set',
        ]
