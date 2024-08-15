from pprint import pprint
from collections import defaultdict

from o2lib.models.dictlist import queryset2dictlist

from bordado.models import Pedido


__all__ = ['get_totais_pedidos']


def get_totais_pedidos(cliente=None):
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

    totais = defaultdict(int)

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

    return dict(totais)
