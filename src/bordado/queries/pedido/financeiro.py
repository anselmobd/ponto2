from decimal import Decimal
from pprint import pprint

from o2lib.models.dictlist import queryset2dictlist

from bordado.models import Pedido


__all__ = ['get_pedido_financeiro']


def get_pedido_financeiro(cliente=None):
    query = Pedido.objects

    if cliente:
        query = query.filter(
            cliente=cliente
        )

    query = query.values(
        'numero',
        'pedidoitem__quantidade',
        'pedidoitem__preco',
        'pedidoitem__programacao',
        'pedidoitem__ajuste',
        'pedidoitem__cobrancas__cobranca',
    )

    pedido_data = queryset2dictlist(query)

    zero = Decimal('0.00')
    totais = {
        'fechado': zero,
        'cobrado': zero,
    }

    for row in pedido_data:
        row['valor'] = (
            row['pedidoitem__quantidade'] * row['pedidoitem__preco']
            + row['pedidoitem__programacao']
            + row['pedidoitem__ajuste']
        )
        status = (
            'fechado'
            if row['pedidoitem__cobrancas__cobranca'] is None
            else 'cobrado'
        )
        totais[status] += row['valor']

    return totais
