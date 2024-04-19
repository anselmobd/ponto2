from django.urls import include, path
from rest_framework import routers

from .views.main import (
    index,
    menu,
    menu_puro,
    sobre,
    sobre_puro,
)
from .views.lancamento import Financeiro
from .api.rest import (
    ApontamentoProducaoViewSet,
    BordadoViewSet,
    ClienteViewSet,
    CobrancaViewSet,
    ContatoViewSet,
    DificuldadeBordadoViewSet,
    FormaPagamentoViewSet,
    LancamentoViewSet,
    OrdemProducaoViewSet,
    PedidoItemCobrancaViewSet,
    PedidoItemViewSet,
    PedidoViewSet,
    TipoComunicacaoViewSet,
    UserViewSet,
)


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'contato', ContatoViewSet)
router.register(r'dificuldade_bordado', DificuldadeBordadoViewSet)
router.register(r'bordado', BordadoViewSet)
router.register(r'pedido', PedidoViewSet)
router.register(r'pedido_item', PedidoItemViewSet)
router.register(r'tipo_comunicacao', TipoComunicacaoViewSet)
router.register(r'forma_pagamento', FormaPagamentoViewSet)
router.register(r'cobranca', CobrancaViewSet)
router.register(r'pedido_item_cobranca', PedidoItemCobrancaViewSet)
router.register(r'lancamento', LancamentoViewSet)
router.register(r'ordem_producao', OrdemProducaoViewSet)
router.register(r'apontamento_producao', ApontamentoProducaoViewSet)

app_name = 'bordado'
urlpatterns = [
    path('api/', include(router.urls)),
    path('tw', menu, name='index'),
    path('', menu_puro, name='index_p'),
    path('old', index, name='index_old'),
    path('sobre_tw', sobre, name='sobre'),
    path('sobre', sobre_puro, name='sobre_p'),
    path('financeiro', Financeiro.as_view(), name='financeiro'),
]
