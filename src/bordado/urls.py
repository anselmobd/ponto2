from django.urls import include, path
from rest_framework import routers

from .views.main import (
    menu,
    index,
    sobre,
)
from .views.financeiro import Financeiro
from .api.rest import (
    ApontamentoProducaoViewSet,
    BordadoViewSet,
    ClienteViewSet,
    CobrancaViewSet,
    ContatoViewSet,
    DificuldadeBordadoViewSet,
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
router.register(r'cobranca', CobrancaViewSet)
router.register(r'pedido_item_cobranca', PedidoItemCobrancaViewSet)
router.register(r'lancamento', LancamentoViewSet)
router.register(r'ordem_producao', OrdemProducaoViewSet)
router.register(r'apontamento_producao', ApontamentoProducaoViewSet)

app_name = 'bordado'
urlpatterns = [
    path('api/', include(router.urls)),
    path('', menu, name='index'),
    path('old', index, name='index_old'),
    path('sobre', sobre, name='sobre'),
    path('financeiro', Financeiro.as_view(), name='financeiro'),
]
