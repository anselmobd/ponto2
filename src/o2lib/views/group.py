from pprint import pprint


__all__ = [
    'group_rowspan',
]


def group_rowspan(data, group):
    noSpan = True
    for row in data:
        row['rowspan'] = 1
    inferior = []
    atual = []
    for i in range(len(data)-1, -1, -1):
        atual = [data[i][f] for f in group]
        if atual == inferior:
            noSpan = False
            data[i]['rowspan'] = data[i]['rowspan'] + data[i+1]['rowspan']
            data[i+1]['rowspan'] = 0
        inferior = atual[:]
    if noSpan:
        del list(group)[:]
