from pprint import pprint

from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
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
    **dict_keys_value(
        [a for a in __ACTIONS if a != 'list'],
        extend_schema(
            tags=['lancamento']
        ),
    ),
    list=extend_schema(
        summary="Lista lançamentos",
        description="Lista lançamentos em ordem decrescente de data e id",
        tags=['lancamento'],
        parameters=[
            OpenApiParameter(
                name='tipo_lancamento', 
                description="Filtra os lançamentos por tipo", 
                required=False,
                type=str,
                examples=[
                    OpenApiExample(
                        "Todos",
                        summary="Todos",
                        value=None
                    ),
                    OpenApiExample(
                        "Pagamento",
                        summary="Pagamento",
                        value='pagamento'
                    ),
                    OpenApiExample(
                        "Cobranca",
                        summary="Cobrança",
                        value='cobranca'
                    )
                ],
            ),
            OpenApiParameter(
                name='conciliada', 
                description="Filtra pela conciliação", 
                required=False,
                type=str,
                examples=[
                    OpenApiExample(
                        "Todos",
                        summary="Todos",
                        value=None
                    ),
                    OpenApiExample(
                        "Sim",
                        summary="Sim",
                        value='sim'
                    ),
                    OpenApiExample(
                        "Não",
                        summary="Não",
                        value='nao'
                    )
                ],
            ),
            OpenApiParameter(
                name='ultima_data', 
                description=("Data do par data/id que identifica o registro "
                    "anterior ao primeiro listado"), 
                required=False,
                type=OpenApiTypes.DATE,
            ),
            OpenApiParameter(
                name='ultimo_id', 
                description=("Id do par data/id que identifica o registro "
                    "anterior ao primeiro listado"), 
                required=False,
                type=OpenApiTypes.INT64,
            ),
            OpenApiParameter(
                name='ate_ultimo_aberto', 
                description="Carrega lançamentos até último em aberto", 
                required=False,
                type=str,
                examples=[
                    OpenApiExample(
                        "Desligado",
                        summary="Desligado",
                        value=None
                    ),
                    OpenApiExample(
                        "Ligado",
                        summary="Busca último em aberto e lista até ele",
                        value='s'
                    )
                ],
            ),
        ],
    )
)
class LancamentoViewSet(viewsets.ModelViewSet):
    # queryset = Lancamento.objects.prefetch_related(
    #     'cliente',
    #     'cobranca',
    #     'usuario',
    #     'pagamentocobranca_set',
    # )
    serializer_class = LancamentoFullSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cliente__apelido']

    def get_queryset(self):

        cliente__apelido = self.request.query_params.get(
            'cliente__apelido', None)
        tipo_lancamento = self.request.query_params.get('tipo_lancamento', None)
        conciliada = self.request.query_params.get('conciliada', None)
        ultima_data = self.request.query_params.get('ultima_data', None)
        ultimo_id = self.request.query_params.get('ultimo_id', None)
        ate_ultimo_aberto = self.request.query_params.get(
            'ate_ultimo_aberto', None)
        
        queryset = Lancamento.objects.all()

        queryset = queryset.prefetch_related(
            'cliente',
            'cobranca',
            'usuario',
            'pagamentocobranca_set',
        )

        queryset = queryset.annotate(
            valor_total_recebido=Sum(
                'pagamentos__valor',
                default=0
            ),
            valor_total_pago=Sum(
                'pagamentocobranca__valor',
                default=0
            )
        )

        if ultima_data is not None:
            queryset = queryset.filter(
                data__lte=ultima_data
            )

        if ultimo_id is not None:
            queryset = queryset.exclude(
                data=ultima_data,
                id__gte=ultimo_id,
            )

        if ate_ultimo_aberto is not None:
            ultimo_lancamento = Lancamento.objects.filter(
                cliente__apelido=cliente__apelido
            ).filter(
                pagamentocobranca__isnull=True
            ).filter(
                cobranca__pagamentocobranca__isnull=True
            ).order_by(
                'data',
                'id',
            )
            if ultimo_lancamento:
                queryset = queryset.filter(
                    data__gte=ultimo_lancamento[0].data
                ).exclude(
                    data=ultimo_lancamento[0].data,
                    id__lt=ultimo_lancamento[0].id,
                )
            else:
                queryset = queryset.filter(id=-1)

        if tipo_lancamento is not None:
            if 'pagamento'.startswith(tipo_lancamento):
                queryset = queryset.filter(
                    cobranca__isnull=True
                )
                if conciliada is not None:
                    if 'sim'.startswith(conciliada):
                        queryset = queryset.filter(
                            # pagamentocobranca__isnull=False
                            valor=F('valor_total_pago')
                        )
                    else:  # 'nao'.startswith(conciliada):
                        queryset = queryset.exclude(
                            valor=F('valor_total_pago')
                        )
            else:  # 'cobranca'.startswith(tipo_lancamento):
                queryset = queryset.filter(
                    cobranca__isnull=False
                )
                if conciliada is not None:
                    if 'sim'.startswith(conciliada):
                        queryset = queryset.filter(
                            # cobranca__pagamentocobranca__isnull=False
                            valor=-F('valor_total_recebido')
                        )
                    else:  # 'nao'.startswith(conciliada):
                        queryset = queryset.exclude(
                            valor=-F('valor_total_recebido')
                        )

        # Aplica a ordenação padrão do modelo explicitamente
        return queryset.order_by(*Lancamento._meta.ordering)

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
