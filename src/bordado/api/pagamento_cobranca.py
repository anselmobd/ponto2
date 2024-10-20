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
from bordado.models import (
    PagamentoCobranca,
)
from bordado.serializers.simple.pagamento_cobranca import (
    PagamentoCobrancaSimpleSerializer
)


__all__ = [
    'PagamentoCobrancaViewSet',
]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['pagamento_cobranca'])))
class PagamentoCobrancaViewSet(viewsets.ModelViewSet):
    queryset = PagamentoCobranca.objects.all()
    serializer_class = PagamentoCobrancaSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]
