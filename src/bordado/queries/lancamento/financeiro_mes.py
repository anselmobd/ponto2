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
from django.utils.timezone import now

from o2lib.models.dictlist import queryset2dictlist

from bordado.models import Lancamento


__all__ = ['get_lancamento_financeiro_mes']


def get_lancamento_financeiro_mes(
        cliente=None,
        ano=None,
        mes=None,
        group_by='mes',  ## mes ou cliente
        separa_areceber=False,
        ):

    if group_by == 'mes':
        group_field = 'mes'
        order_by = f'-{group_field}'
    else:
        group_field = 'cliente__apelido'
        order_by = group_field

    query = Lancamento.objects

    if cliente:
        query = query.filter(
            cliente=cliente
        )

    if ano:
        query = query.filter(
            data__year=ano
        )

    if mes:
        query = query.filter(
            data__month=mes
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
        recebido=Q(cobranca__isnull=True),
    )

    if separa_areceber:
        query = query.annotate(
            futuro=ExpressionWrapper(
                Q(data__gt=now().date()),
                output_field=BooleanField()
            )
        )
        query = query.values(group_field, 'recebido', 'futuro')
    else:
        query = query.values(group_field, 'recebido')

    query = query.annotate(
        total=Sum('modulo_valor')
    )

    query = query.order_by(order_by)

    grupo_status = queryset2dictlist(query)

    por_grupo = {}
    for item in grupo_status:
        grupo = item[group_field]
        if item['recebido']:
            status = 'recebido'
        else:
            if separa_areceber:
                status = 'areceber' if item['futuro'] else 'cobrado'
            else:
                status = 'cobrado'
        valor = item['total']
        
        if grupo not in por_grupo:
            por_grupo[grupo] = {
                group_field: grupo,
                'cobrado': Decimal('0.00'),
                'recebido': Decimal('0.00'),
                'areceber': Decimal('0.00'),
            }
        
        por_grupo[grupo][status] += valor

    result = list(por_grupo.values())
    return result
