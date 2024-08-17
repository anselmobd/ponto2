from decimal import Decimal
from pprint import pprint

from django.db.models import (
    CharField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
    Value,
)
from django.db.models.fields import (
    TextField,
    BooleanField,
)
from django.db.models.functions import (
    Cast,
    Concat,
    LPad,
)

from o2lib.models.dictlist import queryset2dictlist

from bordado.models import Pedido


__all__ = ['financeiro_por_mes']


def financeiro_por_mes(cliente=None):
    query = Pedido.objects

    if cliente:
        query = query.filter(
            cliente=cliente
        )

    query = query.annotate(
        mes=Concat(
            'entrega__year',
            Value('-'),
            LPad(
                Cast('entrega__month', TextField()),
                2,
                Cast(0, TextField()),
            ),
            output_field=CharField()
        )
    )

    query = query.annotate(
        valor=(
            F('pedidoitem__quantidade') * F('pedidoitem__preco') +
            F('pedidoitem__programacao') +
            F('pedidoitem__ajuste')
        )
    )

    query = query.annotate(
        cobrado=ExpressionWrapper(
            Q(pedidoitem__cobrancas__cobranca__isnull=False),
            output_field=BooleanField()
        )
    )

    query = query.values('mes', 'cobrado')

    query = query.annotate(
        total=Sum('valor')
    )

    query = query.order_by('-mes')

    mes_status = queryset2dictlist(query)

    por_mes = {}
    for item in mes_status:
        mes = item['mes']
        status = 'cobrado' if item['cobrado'] else 'fechado'
        valor = item['total']
        
        if mes not in por_mes:
            por_mes[mes] = {
                'mes': mes,
                'cobrado': Decimal('0.00'),
                'fechado': Decimal('0.00'),
            }
        
        por_mes[mes][status] = valor

    result = list(por_mes.values())
    return result
