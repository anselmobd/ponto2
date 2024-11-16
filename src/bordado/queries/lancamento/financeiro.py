from decimal import Decimal
from pprint import pprint

from django.db.models import (
    ExpressionWrapper,
    Q,
)
from django.db.models.fields import (
    BooleanField,
)
from django.utils.timezone import now

from o2lib.models.dictlist import queryset2dictlist

from bordado.models.lancamento import Lancamento


__all__ = ['get_lancamento_financeiro']


def get_lancamento_financeiro(cliente=None):
    query = Lancamento.objects

    if cliente:
        query = query.filter(
            cliente=cliente
        )

    query = query.annotate(
        futuro=ExpressionWrapper(
            Q(data__gt=now().date()),
            output_field=BooleanField()
        )
    )

    query = query.values(
        'id',
        'cobranca',
        'valor',
        'futuro',
    )

    pedido_data = queryset2dictlist(query)

    zero = Decimal('0.00')
    totais = {
        'cobrado': zero,
        'recebido': zero,
        'areceber': zero,
    }

    for row in pedido_data:
        if row['cobranca'] is None:
            totais['recebido'] += row['valor']
        else:
            if row['futuro']:
                totais['areceber'] += -row['valor']
            else:
                totais['cobrado'] += -row['valor']

    return totais
