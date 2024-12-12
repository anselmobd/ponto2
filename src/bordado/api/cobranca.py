import datetime
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

from o2lib.datetime.convert import parcelas_str2int_list
from o2lib.dict import dict_keys_value
from o2lib.number import parcela_i_de_n_de_valor

from bordado.api.rest_consts import __ACTIONS
from bordado.models import (
    Cliente,
    Cobranca,
    Lancamento,
    PedidoItem,
    PedidoItemCobranca,
)
from bordado.serializers.full.cobranca import CobrancaSerializer

__all__ = [
    'CobrancaViewSet',
]


@extend_schema_view(
    **dict_keys_value(__ACTIONS, extend_schema(tags=['cobranca'])))
class CobrancaViewSet(viewsets.ModelViewSet):
    queryset = Cobranca.objects.prefetch_related(
        'cliente',
        'comunicacao',
        'usuario',
        'pedidoitemcobranca_set',
        'lancamento_set',
        'pagamentocobranca_set',
    )
    serializer_class = CobrancaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cliente__apelido']

    def create(self, request, *args, **kwargs):
        if 'pedidos_itens' in request.data:
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
                    cobranca = Cobranca(
                        cliente=cliente,
                        informacao=request.data.get('informacao'),
                        comunicacao_id=request.data.get('comunicacao_id'),
                        nf=request.data.get('nf'),
                        valor=request.data.get('valor'),
                        data=request.data.get('data'),
                        parcelamento=request.data.get('parcelamento'),
                        usuario=self.request.user,
                    )
                    cobranca.save()
                except Exception as e:
                    errors['human'].append("Erro ao criar o registro de cobrança.")
                    errors['tech'].append(repr(e))
                    raise TypeError

                total_cobrado = cobranca.valor
                for pedido_item_id in request.data['pedidos_itens']:
                    try:
                        pedido_item = PedidoItem.objects.get(id=pedido_item_id)
                    except Exception as e:
                        errors['human'].append("Erro ao buscar por pedido marcado.")
                        errors['tech'].append(repr(e))
                        raise TypeError
                    
                    pedido_item_valor = (
                        (pedido_item.quantidade * pedido_item.preco) +
                        pedido_item.programacao +
                        pedido_item.ajuste
                    )
                    pedido_item_cobranca_valor = min(pedido_item_valor, total_cobrado)

                    if (pedido_item_cobranca_valor):
                        try:
                            pedido_item_cobranca = PedidoItemCobranca(
                                pedido_item=pedido_item,
                                cobranca=cobranca,
                                valor=pedido_item_cobranca_valor
                            )
                            pedido_item_cobranca.save()
                        except Exception as e:
                            errors['human'].append("Erro ao inserir registro que liga cobrança ao pedido.")
                            errors['tech'].append(repr(e))
                            raise TypeError
                        total_cobrado -= float(pedido_item_cobranca_valor)

                try:
                    cobranca_data = datetime.datetime.strptime(
                        cobranca.data, "%Y-%m-%d").date()
                except Exception as e:
                    errors['human'].append("Erro ao montar data de cobranca.")
                    errors['tech'].append(repr(e))
                    raise TypeError

                try:
                    parcelamento = request.data.get('parcelamento', '')
                    if not parcelamento:
                        parcelas = [0]
                    else:
                        parcelas = parcelas_str2int_list(
                            cobranca_data, parcelamento)
                    n_parcelas = len(parcelas)
                except Exception as e:
                    errors['human'].append("Erro ao montar lista de parcelas.")
                    errors['tech'].append(repr(e))
                    raise TypeError

                if parcelas[0] < 0:
                    errors['human'].append(
                        "Não é possível ter parcela anterior à cobrança.")
                    errors['tech'].append(repr(parcelas))
                    raise TypeError

                for i, parcela in enumerate(parcelas, start=1):
                    try:
                        lancamento = Lancamento(
                            cliente=cliente,
                            data=(
                                cobranca_data +
                                datetime.timedelta(days=parcela)
                            ),
                            cobranca=cobranca,
                            parcela=i,
                            n_parcelas=n_parcelas,
                            valor=-parcela_i_de_n_de_valor(
                                i, n_parcelas, cobranca.valor),
                            usuario=self.request.user,
                        )
                        lancamento.save()
                    except Exception as e:
                        errors['human'].append("Erro ao inserir de lancamento.")
                        errors['tech'].append(repr(e))
                        raise TypeError

                return Response(
                    CobrancaSerializer(cobranca).data,
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)
