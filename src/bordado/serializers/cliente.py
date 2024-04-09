from rest_framework import serializers

from bordado.models import (
    Cliente,
)
from bordado.serializers.simple.user import UserSerializer


__all__ = [
    'ClienteSerializer',
]


class ClienteSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()

    class Meta:
        model = Cliente
        fields = [
            'id',
            'apelido',
            'usuario',
            'quando',
            'nome',
            'fansasia',
            'cnpj9',
            'cnpj4',
            'cnpj2',
            'cep',
            'logradouro',
            'numero',
            'complemento',
            'cidade',
            'uf',
            'boleto',
            'conta_corrente',
            'parcela',
        ]

    def none_if_empty(self, data, field):
        if field in data:
            if isinstance(data[field], str):
                if data[field].strip() == '':
                    data[field] = None

    def to_internal_value(self, data):
        self.none_if_empty(data, 'numero')
        self.none_if_empty(data, 'cnpj9')
        self.none_if_empty(data, 'cnpj4')
        self.none_if_empty(data, 'cnpj2')
        return super().to_internal_value(data)
