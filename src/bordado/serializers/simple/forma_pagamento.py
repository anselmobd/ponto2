from django.contrib.auth.models import User
from rest_framework import serializers

from bordado.models import (
    FormaPagamento,
)


__all__ = [
    'FormaPagamentoSerializer',
]


class FormaPagamentoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPagamento
        fields = [
            'id',
            'nome',
        ]
