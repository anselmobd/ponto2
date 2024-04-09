from pprint import pprint

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from rest_framework import (
    permissions,
    viewsets,
    status,
)
from rest_framework.response import Response

from o2lib.dict import dict_keys_value

from bordado.api.rest_consts import __ACTIONS
from bordado.models import (
    Cliente,
    Lancamento,
)
from bordado.serializers.full.lancamento import LancamentoFullSerializer


__all__ = [
    'LancamentoViewSet',
]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['lancamento'])))
class LancamentoViewSet(viewsets.ModelViewSet):
    queryset = Lancamento.objects.all()
    serializer_class = LancamentoFullSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cliente__apelido']

    def create(self, request, *args, **kwargs):
        if len(request.data.keys()) == 4:
            try:
                errors = {
                    'human': [],
                    'tech': [],
                }

                try:
                    cliente = Cliente.objects.get(
                        apelido=request.data['cliente']['apelido']
                    )
                except KeyError as e:
                    errors['human'].append("Informe apelido de cliente.")
                    errors['tech'].append(repr(e))
                    raise TypeError

                try:
                    lancamento = Lancamento(
                        cliente=cliente,
                        data=request.data.get('data'),
                        informacao=request.data.get('informacao'),
                        valor=request.data.get('valor'),
                        usuario=self.request.user,
                    )
                    lancamento.save()
                except Exception as e:
                    errors['human'].append("Erro ao criar o registro de lancamento.")
                    errors['tech'].append(repr(e))
                    raise TypeError

                return Response(
                    self.serializer_class(lancamento).data,
                    status=status.HTTP_201_CREATED,
                )
            except Exception:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)
