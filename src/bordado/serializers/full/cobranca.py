from rest_framework import serializers

from bordado.models import (
    Cobranca,
    Bordado,
    Lancamento,
    Pedido,
    PedidoItem,
    PedidoItemCobranca,
)

from bordado.serializers.cliente import ClienteSerializer
from bordado.serializers.dificuldade_bordado import DificuldadeBordadoSerializer
from bordado.serializers.simple.user import UserSerializer
from bordado.serializers.simple.tipo_comunicacao import TipoComunicacaoSerializer


class PedidoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    class Meta:
        model = Pedido
        fields = [
            'numero',
            'cliente',
            'inserido_em',
            'entrega',
            'cancelado',
        ]

class BordadoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
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
    pedido = PedidoSerializer()
    bordado = BordadoSerializer()
    usuario = UserSerializer()

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
    cliente = ClienteSerializer()
    usuario = UserSerializer()

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
    cliente = ClienteSerializer()
    comunicacao = TipoComunicacaoSerializer()
    usuario = UserSerializer()
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
