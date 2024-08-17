from decimal import Decimal
from pprint import pprint

from django.db.models import (
    Case,
    CharField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
    Value,
    When,
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

from bordado.models import Lancamento


__all__ = ['get_lancamento_financeiro_mes']


def get_lancamento_financeiro_mes(cliente=None):
    query = Lancamento.objects

    if cliente:
        query = query.filter(
            cliente=cliente
        )

    query = query.annotate(
        mes=Concat(
            'data__year',
            Value('-'),
            LPad(
                Cast('data__month', TextField()),
                2,
                Cast(0, TextField()),
            ),
            output_field=CharField()
        )
    )

    query = query.annotate(
        modulo_valor=Case(
            When(
                ExpressionWrapper(
                    Q(cobranca__isnull=False),
                    output_field=BooleanField()
                ),
                then=-F('valor')
            ),
            default='valor',
            # output_field=models.SmallIntegerField(),
        )
    )

    query = query.annotate(
        recebido=Q(cobranca__isnull=False),
    )

    query = query.values('mes', 'recebido')

    query = query.annotate(
        total=Sum('modulo_valor')
    )

    query = query.order_by('-mes')

    mes_status = queryset2dictlist(query)

    por_mes = {}
    for item in mes_status:
        mes = item['mes']
        status = 'recebido' if item['recebido'] else 'cobrado'
        valor = item['total']
        
        if mes not in por_mes:
            por_mes[mes] = {
                'mes': mes,
                'cobrado': Decimal('0.00'),
                'recebido': Decimal('0.00'),
            }
        
        por_mes[mes][status] = valor

    result = list(por_mes.values())
    return result
