from .util import append, find, operation


def do_ingress(p4, flow):
    ingress = find(
        p4['pipelines'],
        lambda item: item['name'] == 'ingress',
    )
    table_name = ingress['init_table']

    while table_name is not None:
        table = find(
            ingress['tables'],
            lambda item: item['name'] == table_name,
        )

        if table is not None:
            key, *_ = table['key']
            if key['match_type'] == 'valid':
                raise NotImplementedError('Tarefa 2')

            append(flow, key['target'], 'U')

            # match_type true/false ??
            table_name = None # temp

        else:  # table não localizada
            conditional = find(
                ingress['conditionals'],
                lambda item: item['name'] == table_name,
            )
            operation(conditional['expression'], flow)

            # conditional true/false ??
            table_name = conditional['true_next']  # temp
