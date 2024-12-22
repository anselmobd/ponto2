from decimal import Decimal
from functools import lru_cache
from pprint import pprint


__all__ = [
    'parcela_i_de_n_de_valor',
    'valor_proporcional',
    'decimal_proporcional',
]


@lru_cache
def parcela_i_de_n_de_valor(n, m, valor, decimais=2):
    try:
        parcela = round(valor / m, decimais)
    except ZeroDivisionError:
        parcela = 0.0
    if n == m:
        return valor - (parcela * (m - 1))
    else:
        return parcela


@lru_cache
def valor_proporcional(valor, proporcao, total, decimais=2):
    proporcional = 0.0
    if valor:
        try:
            proporcional = round(
                valor * proporcao / total,
                decimais
            )
        except ZeroDivisionError:
            ...
    return proporcional
  

@lru_cache
def decimal_proporcional(valor, proporcao, total, decimais=2):
    return Decimal(
        valor_proporcional(valor, proporcao, total, decimais)
    ).quantize(
        Decimal(f'0.{"0" * decimais}1'),
        rounding='ROUND_HALF_UP'
    )
