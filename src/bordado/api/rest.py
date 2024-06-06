from pprint import pprint

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from rest_framework import (
    generics,
    permissions,
    viewsets,
)

from o2lib.dict import dict_keys_value

from bordado.api.cobranca import CobrancaViewSet
from bordado.api.pedido_item import PedidoItemViewSet
from bordado.api.lancamento import LancamentoViewSet
from bordado.api.rest_consts import __ACTIONS
from bordado.models import (
    ApontamentoProducao,
    Bordado,
    Cliente,
    Contato,
    DificuldadeBordado,
    FormaPagamento,
    OrdemProducao,
    Pedido,
    PedidoItem,
    PedidoItemCobranca,
    TipoComunicacao,
)
from bordado.serializers import (
    ApontamentoProducaoSerializer,
    BordadoSerializer,
    DificuldadeBordadoSerializer,
    OrdemProducaoSerializer,
    PedidoItemCobrancaSerializer,
    PedidoItemSerializer,
    PedidoSerializer,
    UserSerializer,
)
from bordado.serializers.simple.tipo_comunicacao import TipoComunicacaoSimpleSerializer
from bordado.serializers.simple.forma_pagamento import FormaPagamentoSimpleSerializer
from bordado.serializers.down.cliente import ClienteDownSerializer
from bordado.serializers.down.contato import ContatoDownSerializer


__all__ = [
    'ApontamentoProducaoViewSet',
    'BordadoViewSet',
    'ClienteViewSet',
    'CobrancaViewSet',
    'DificuldadeBordadoViewSet',
    'LancamentoViewSet',
    'OrdemProducaoViewSet',
    'PedidoItemCobrancaViewSet',
    'PedidoItemViewSet',
    'PedidoViewSet',
    'TipoComunicacaoViewSet',
    'UserViewSet',
]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['user'])))
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['cliente'])))
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteDownSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
        

@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['contato'])))
class ContatoViewSet(viewsets.ModelViewSet):
    queryset = Contato.objects.all()
    serializer_class = ContatoDownSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['dificuldade_bordado'])))
class DificuldadeBordadoViewSet(viewsets.ModelViewSet):
    queryset = DificuldadeBordado.objects.all()
    serializer_class = DificuldadeBordadoSerializer
    permission_classes = [permissions.IsAuthenticated]

@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['bordado'])))
class BordadoViewSet(viewsets.ModelViewSet):
    queryset = Bordado.objects.all()
    serializer_class = BordadoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['cliente__apelido', 'nome']


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['pedido'])))
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['pedido_item_cobranca'])))
class PedidoItemCobrancaViewSet(viewsets.ModelViewSet):
    queryset = PedidoItemCobranca.objects.all()
    serializer_class = PedidoItemCobrancaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pedido_item__pedido__cliente__apelido']


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['apontamento_producao'])))
class ApontamentoProducaoViewSet(viewsets.ModelViewSet):
    queryset = ApontamentoProducao.objects.all()
    serializer_class = ApontamentoProducaoSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['ordem_producao'])))
class OrdemProducaoViewSet(viewsets.ModelViewSet):
    queryset = OrdemProducao.objects.all()
    serializer_class = OrdemProducaoSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['tipo_comunicacao'])))
class TipoComunicacaoViewSet(viewsets.ModelViewSet):
    queryset = TipoComunicacao.objects.all()
    serializer_class = TipoComunicacaoSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['forma_pagamento'])))
class FormaPagamentoViewSet(viewsets.ModelViewSet):
    queryset = FormaPagamento.objects.all()
    serializer_class = FormaPagamentoSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]
