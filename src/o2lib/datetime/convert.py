import datetime
from pprint import pprint

from o2lib.strings import split_non_empty


__all__ = [
    'parcelas_str2int_list'
]


def parcelas_str2int_list(dt, text):
    """
    Retorna: Lista de inteiros indicando dias de parcelamento com referencia à
    uma data base
    Recebe:
        dt = data base
        text = string contendo informações sobre parcelamento, com parcelas
            separadas por espaço
    Depois do split mo text, cada pedado de informação pode ser:
        string contendo apenas interos = dias da parcela após a data base
        string contendo o caractere "/" = indicação direta de uma data do 
            parcelamento
    Quanto string indica diretamente uma data, pode ser nos seguintes formatos:
        d/ : onde d é indica o dia no mês da data base
            d pode ter 1 ou 2 dígitos
        d/m : onde d/m é indica o dia e mês, entre a data base e um ano após
            d e m podem ter 1 ou 2 dígitos
        d/m/a : onde d/m/a é indica diretamente dia, mês e ano
            d e m podem ter 1 ou 2 dígitos; a pode ter 2 ou 4 dígitos
    """
    parcelas_str = split_non_empty(text)
    parcelas_int = []
    for parcela_str in parcelas_str:
        if parcela_str:
            if "/" in parcela_str:
                dia, *mes_ano = parcela_str.split("/")
                dia = int(dia)
                mes = dt.month
                ano = dt.year
                if mes_ano:
                    if mes_ano[0]:
                        mes = int(mes_ano[0])
                    if len(mes_ano) == 2:
                        ano = int(mes_ano[1])
                        if ano <= 99:
                            ano += 2000
                dt_parcela = datetime.date(ano, mes, dia)
                if dt_parcela < dt:
                    try:
                        dt_parcela = dt_parcela.replace(year=dt_parcela.year+1)
                    except ValueError:
                        dt_parcela = datetime.date(dt_parcela.year+1, 2, 28)
                parcelas_int.append((dt_parcela - dt).days)
            else:
                parcelas_int.append(int(parcela_str))

    return sorted(parcelas_int)
