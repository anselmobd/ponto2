from django.contrib.auth.models import User
from rest_framework import serializers

from bordado.models import (
    Cliente,
    Contato,
    FormaPagamento,
    TipoComunicacao,
)
from bordado.serializers.simple.tipo_comunicacao import TipoComunicacaoSimpleSerializer
from bordado.serializers.simple.forma_pagamento import FormaPagamentoSimpleSerializer


__all__ = [
    'ClienteDownSerializer',
]



class ContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contato
        fields = [
            'id',
            'nome',
            'telefone',
            'email',
            'preferencial',
        ]


class ClienteDownSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    comunicacao = serializers.PrimaryKeyRelatedField(queryset=TipoComunicacao.objects.all(), required=False)
    comunicacao_obj = serializers.SerializerMethodField()
    forma_pagamento = serializers.PrimaryKeyRelatedField(queryset=FormaPagamento.objects.all(), required=False)
    forma_pagamento_obj = serializers.SerializerMethodField()
    contato_set = ContatoSerializer(many=True, read_only=True)

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
            'forma_pagamento',
            'forma_pagamento_obj',
            'conta_corrente',
            'contato_set',
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

    def get_forma_pagamento_obj(self, obj):
        if obj.forma_pagamento:
            return FormaPagamentoSimpleSerializer(obj.forma_pagamento).data
        return None
