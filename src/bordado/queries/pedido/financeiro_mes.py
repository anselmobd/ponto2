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
    Round,
)

from o2lib.models.dictlist import queryset2dictlist

from bordado.models import Pedido


__all__ = ['get_pedido_financeiro_mes']


def get_pedido_financeiro_mes(
        cliente=None,
        ano=None,
        mes=None,
        group_by='mes',  ## mes ou cliente
        ):

    if group_by == 'mes':
        group_field = 'mes'
        order_by = f'-{group_field}'
    else:
        group_field = 'cliente__apelido'
        order_by = group_field

    query = Pedido.objects

    if cliente:
        query = query.filter(
            cliente=cliente
        )

    if ano:
        query = query.filter(
            entrega__year=ano
        )

    if mes:
        query = query.filter(
            entrega__month=mes
        )

    query = query.filter(
        entrega__isnull=False
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
        valor=Round(
            F('pedidoitem__quantidade') * F('pedidoitem__preco') +
            F('pedidoitem__programacao') +
            F('pedidoitem__ajuste'),
            precision=2
        )
    )

    query = query.annotate(
        cobrado=ExpressionWrapper(
            Q(pedidoitem__cobrancas__cobranca__isnull=False),
            output_field=BooleanField()
        )
    )

    query = query.values(group_field, 'cobrado')

    query = query.annotate(
        total=Sum('valor')
    )

    query = query.order_by(order_by)

    grupo_status = queryset2dictlist(query)

    por_grupo = {}
    for item in grupo_status:
        grupo = item[group_field]
        status = 'cobrado' if item['cobrado'] else 'fechado'
        valor = item['total']
        
        if grupo not in por_grupo:
            por_grupo[grupo] = {
                group_field: grupo,
                'cobrado': Decimal('0.00'),
                'fechado': Decimal('0.00'),
            }
        
        por_grupo[grupo][status] = valor

    result = list(por_grupo.values())
    return result
