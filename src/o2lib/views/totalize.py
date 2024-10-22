from datetime import date
from pprint import pprint


__all__ = [
    'totalize_data',
    'get_total_row',
    'totalize_grouped_data',
]


def totalize_data(data, config, return_not_append=False):
    '''
    Exemplos de uso do row_if
        'row_if': 'field',
            equivale a
        'row_if': {'*': {True: 'field'}},

        'row_if': {'*': {False: 'field'}},

        'row_if': {
            'field_1': {False: 'field_2', True: 'field_3'},
            'field_4': {False: 'field_5', True: 'field_6'},
        },

    '''
    if 'flags' in config and 'NO_TOT_1' in config['flags']:
        if len(data) < 2:
            return

    all_keys = data[0].keys()
    totrow = {key: '' for key in all_keys}

    if 'row_style' in config:
        totrow['|STYLE'] = config['row_style']

    totrow['|CLASS'] = 'totalizador'

    if 'class_suffix' in config:
        class_suffix = config['class_suffix']
        keys = [key for key in all_keys if '|' not in key]
        for key in keys:
            totrow[f'{key}|CLASS'] = f'{key}{class_suffix}'

    for key in config['sum']:
        totrow[key] = 0

    row_if = config.get('row_if', {})
    if not isinstance(row_if, dict):
        row_if = {
            key: {True: row_if}
            for key in config['sum']
        }
    if row_if:
        if '*' in row_if:
            for key in config['sum']:
                if key not in row_if:
                    row_if[key] = row_if['*'].copy()
            del(row_if['*'])
        for key in config['sum']:
            if key not in row_if:
                row_if[key] = None
        def do_sum(row, key):
            return (
                row_if[key] is None or
                all([
                    bool_key == bool(row[row_if[key][bool_key]])
                    for bool_key in row_if[key]
                ])
            )
    else:
        def do_sum(row, key):
            return True

    for row in data:
        for key in config['sum']:
            if do_sum(row, key):
                totrow[key] += row[key]

    if 'descr' in config:
        for key in config['descr']:
            totrow[key] = config['descr'][key]

    if 'count' in config:
        for key in config['count']:
            totrow[key] = len(data)

    if return_not_append:
        return totrow
    else:
        data.append(totrow)


def get_total_row(data, config):
    return totalize_data(data, config, return_not_append=True)


def totalize_grouped_data(data, config):

    def copy_init_clean(row_ori, empty, not_fields, clean_pipe):
        row = row_ori.copy()
        del_keys = []
        for key in row:
            if key not in not_fields:
                row[key] = empty
            if clean_pipe:
                if '|' in key:
                    del_keys.append(key)
        for key in del_keys:
            del row[key]
        return row

    empty = config['empty'] if 'empty' in config else ''
    clean_pipe = config['clean_pipe'] if 'clean_pipe' in config else False

    temp_end_row = copy_init_clean(data[0], empty, [], clean_pipe)
    data.append(temp_end_row)

    if 'global_sum' in config:
        global_count = 0
        global_tot = temp_end_row.copy()
        if 'global_descr' not in config:
            config['global_descr'] = config['descr']
        for key in config['global_descr']:
            global_tot[key] = config['global_descr'][key]
        for key in config['global_sum']:
            global_tot[key] = 0

    for key in config['sum']:
        temp_end_row[key] = 0

    totrows = {}
    group_values = {}
    init_group = True
    for row_idx, row in enumerate(data):
        do_sum = True
        if 'row_if' in config:
            do_sum = row[config['row_if']]
        do_global_sum = True
        if 'global_row_if' in config:
            do_global_sum = row[config['global_row_if']]

        if not init_group:
            if list_key != [row[key] for key in config['group']]:
                for key in config['descr']:
                    totrow[key] = config['descr'][key].format(**group_values)
                for key in sum:
                    totrow[key] = sum[key]
                for key in config.get('count', []):
                    totrow[key] = group_count
                total = True
                if 'flags' in config and 'NO_TOT_1' in config['flags']:
                    total = group_count > 1
                if total:
                    if do_global_sum:
                        totrows[row_idx] = totrow
                init_group = True

        if init_group:
            group_count = 0
            list_key = [row[key] for key in config['group']]
            totrow = copy_init_clean(row, empty, config['group'], clean_pipe)
            sum = {key: 0 for key in config['sum']}
            for key in config['group']:
                if isinstance(row[key], date):
                    value = f"{row[key]:%d/%m/%Y}"
                else:
                    value = row[key]
                group_values[key] = value
            init_group = False

        for key in sum:
            if do_sum:
                sum[key] += row[key]
        group_count += 1

        if 'global_sum' in config:
            global_count += 1
            for key in config['global_sum']:
                global_tot[key] += row[key]

    for i in range(len(data)-1, 0, -1):
        if i in totrows:
            if 'row_style' in config:
                totrows[i]['|STYLE'] = config['row_style']
            data.insert(i, totrows[i])

    if 'global_sum' in config:
        total = True
        if 'flags' in config and 'NO_TOT_1' in config['flags']:
            total = global_count > 2  # por conta do temp_end_row
        if total:
            if 'row_style' in config:
                global_tot['|STYLE'] = config['row_style']
            data.insert(len(data)-1, global_tot)

    del(data[len(data)-1])
