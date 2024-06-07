from pprint import pprint

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from rest_framework import (
    permissions,
    viewsets,
)

from o2lib.dict import dict_keys_value

from bordado.api.rest_consts import __ACTIONS
from bordado.models import Bordado
from bordado.serializers import BordadoSerializer
from bordado.serializers.simple.bordado import BordadoSimpleSerializer


__all__ = [
    'BordadoFullViewSet',
    'BordadoViewSet',
]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['bordado'])))
class BordadoViewSet(viewsets.ModelViewSet):
    queryset = Bordado.objects.all()
    serializer_class = BordadoSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['id', 'cliente__apelido', 'nome', 'codigo']


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['bordado__full'])))
class BordadoFullViewSet(viewsets.ModelViewSet):
    queryset = Bordado.objects.all()
    serializer_class = BordadoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['id', 'cliente__apelido', 'nome', 'codigo']
