from django.urls import include, path, re_path
from rest_framework import routers

from bordado.api.bordado import (
    BordadoFullViewSet,
    BordadoViewSet,
)
from bordado.api.rest import (
    ApontamentoProducaoViewSet,
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
from bordado.views.analise.cobranca import AnaliseCobrancaView
from bordado.views.listagem.cobranca import ListagemCobrancaView
from bordado.views.listagem.lancamento import LancamentoView
from bordado.views.listagem.nota_fiscal import NotaFiscalView
from bordado.views.listagem.pedido import PedidoView
from bordado.views.main import (
    index,
    sobre,
)


router = routers.DefaultRouter()
router.register(r'apontamento_producao', ApontamentoProducaoViewSet)
router.register(r'bordado__full', BordadoFullViewSet, 'bordado full')
router.register(r'bordado', BordadoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'cobranca', CobrancaViewSet)
router.register(r'contato', ContatoViewSet)
router.register(r'dificuldade_bordado', DificuldadeBordadoViewSet)
router.register(r'forma_pagamento', FormaPagamentoViewSet)
router.register(r'lancamento', LancamentoViewSet)
router.register(r'ordem_producao', OrdemProducaoViewSet)
router.register(r'pedido_item_cobranca', PedidoItemCobrancaViewSet)
router.register(r'pedido_item', PedidoItemViewSet)
router.register(r'pedido', PedidoViewSet)
router.register(r'tipo_comunicacao', TipoComunicacaoViewSet)
router.register(r'users', UserViewSet)

app_name = 'bordado'
urlpatterns = [
    # API
    path('api/', include(router.urls)),

    # Básicos
    path('', index, name='index'),
    path('sobre', sobre, name='sobre'),

    # Listagem
    re_path(
        r'^listagem_cobranca/(?P<numero>.+)?/?$',
        ListagemCobrancaView.as_view(),
        name='listagem_cobranca',
    ),
    re_path(
        r'^listagem_faturamento/(?P<nf>.+)?/?$',
        NotaFiscalView.as_view(),
        name='listagem_faturamento',
    ),
    path(
        'listagem_lancamento',
        LancamentoView.as_view(),
        name='listagem_lancamento',
    ),
    re_path(
        r'^listagem_pedido/(?P<numero>.+)?/?$',
        PedidoView.as_view(),
        name='listagem_pedido',
    ),

    # Análise
    path(
        'analise_cobranca',
        AnaliseCobrancaView.as_view(),
        name='analise_cobranca',
    ),
]
