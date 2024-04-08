from django.contrib.auth.models import User
from rest_framework import serializers

from bordado.models import (
    DificuldadeBordado,
)


__all__ = [
    'DificuldadeBordadoSerializer',
]


class DificuldadeBordadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DificuldadeBordado
        fields = [
            'id',
            'ordem',
            'descricao',
        ]
