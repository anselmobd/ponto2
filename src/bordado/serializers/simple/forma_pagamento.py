from rest_framework import serializers

from bordado.models import (
    FormaPagamento,
)


__all__ = [
    'FormaPagamentoSimpleSerializer',
]


class FormaPagamentoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPagamento
        fields = [
            'id',
            'nome',
        ]
