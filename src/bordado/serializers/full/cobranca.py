from rest_framework import serializers

# from django.db.models import Sum

from bordado.models import (
    Cobranca,
    Lancamento,
    # PagamentoCobranca,
    PedidoItemCobranca,
)
from bordado.serializers.down.cliente import ClienteDownSerializer
from bordado.serializers.down.pedido_item import PedidoItemDownSerializer
from bordado.serializers.simple.tipo_comunicacao import (
    TipoComunicacaoSimpleSerializer)
from bordado.serializers.simple.user import UserSimpleSerializer


# class PagamentoCobrancaSerializer(serializers.ModelSerializer):
#     inserido_por = UserSimpleSerializer()
#     alterado_por = UserSimpleSerializer()

#     class Meta:
#         model = PagamentoCobranca
#         fields = [
#             'id',
#             'pagamento',
#             'valor',
#             'inserido_em',
#             'inserido_por',
#             'alterado_em',
#             'alterado_por',
#         ]


class PedidoItemCobrancasSerializer(serializers.ModelSerializer):
    pedido_item = PedidoItemDownSerializer()

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
    pedidoitemcobranca_set = PedidoItemCobrancasSerializer(
        many=True, read_only=True)
    lancamento_set = LancamentoSerializer(
        many=True, read_only=True)
    # pagamentocobranca_set = PagamentoCobrancaSerializer(
    #     many=True, read_only=True)
    # valor_total_recebido = serializers.SerializerMethodField()
    
    # def get_valor_total_recebido(self, instance):
    #     return PagamentoCobranca.objects.filter(
    #         cobranca=instance
    #     ).aggregate(
    #         total=Sum('valor', default=0)
    #     )['total']

    class Meta:
        model = Cobranca
        fields = [
            'id',
            'cliente',
            'valor',
            'informacao',
            'comunicacao',
            'nf',
            'data',
            'parcelamento',
            'usuario',
            'quando',
            'pedidoitemcobranca_set',
            'lancamento_set',
            # 'pagamentocobranca_set',
            # 'valor_total_recebido',
        ]
