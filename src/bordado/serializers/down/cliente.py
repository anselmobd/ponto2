from django.contrib.auth.models import User
from rest_framework import serializers

from bordado.models import (
    Cliente,
    TipoComunicacao,
)
from bordado.serializers.simple.tipo_comunicacao import TipoComunicacaoSimpleSerializer


__all__ = [
    'ClienteDownSerializer',
]


class ClienteDownSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    comunicacao = serializers.PrimaryKeyRelatedField(queryset=TipoComunicacao.objects.all())
    comunicacao_obj = serializers.SerializerMethodField()

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
            'bairro',
            'cidade',
            'uf',
            'comunicacao',
            'comunicacao_obj',
            'parcelamento',
            'boleto',
            'conta_corrente',
        ]

    def none_if_empty_str(self, data, field):
        if field in data:
            if isinstance(data[field], str):
                if data[field].strip() == '':
                    data[field] = None

    def to_internal_value(self, data):
        self.none_if_empty_str(data, 'numero')
        self.none_if_empty_str(data, 'cnpj9')
        self.none_if_empty_str(data, 'cnpj4')
        self.none_if_empty_str(data, 'cnpj2')
        return super().to_internal_value(data)

    def get_comunicacao_obj(self, obj):
        if obj.comunicacao:
            return TipoComunicacaoSimpleSerializer(obj.comunicacao).data
        return None
