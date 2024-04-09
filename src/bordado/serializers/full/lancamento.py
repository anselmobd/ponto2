from rest_framework import serializers

from bordado.models import (
    Bordado,
    Cobranca,
    Lancamento,
    Pedido,
    PedidoItem,
    PedidoItemCobranca,
)

from bordado.serializers.dificuldade_bordado import DificuldadeBordadoSerializer
from bordado.serializers.down.cliente import ClienteDownSerializer
from bordado.serializers.down.pedido import PedidoDownSerializer
from bordado.serializers.simple.tipo_comunicacao import TipoComunicacaoSimpleSerializer
from bordado.serializers.simple.user import UserSimpleSerializer


class BordadoSerializer(serializers.ModelSerializer):
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


class PedidoItemSerializer(serializers.ModelSerializer):
    pedido = PedidoDownSerializer()
    bordado = BordadoSerializer()
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


class CobrancaSerializer(serializers.ModelSerializer):
    cliente = ClienteDownSerializer()
    comunicacao = TipoComunicacaoSimpleSerializer()
    usuario = UserSimpleSerializer()
    pedidoitemcobranca_set = PedidoItemCobrancasSerializer(many=True, read_only=True)

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
        ]


class LancamentoFullSerializer(serializers.ModelSerializer):
    cliente = ClienteDownSerializer()
    cobranca = CobrancaSerializer()
    usuario = UserSimpleSerializer()

    class Meta:
        model = Lancamento
        fields = [
            'id',
            'cliente',
            'data',
            'cobranca',
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
