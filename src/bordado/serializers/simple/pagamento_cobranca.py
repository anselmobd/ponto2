from rest_framework import serializers

from bordado.models import (
    PagamentoCobranca,
)


__all__ = [
    'PagamentoCobrancaSimpleSerializer',
]


class PagamentoCobrancaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagamentoCobranca
        fields = '__all__'
