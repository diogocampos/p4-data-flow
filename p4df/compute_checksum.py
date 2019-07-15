from .util import append, find

def do_compute_checksum(p4, flow):
    for checksum in p4['checksums']:
        calculation = find(
            p4['calculations'],
            lambda item: item['name'] == checksum['calculation'],
        )

        for input in calculation['input']:
            if input['type'] == 'field':
                append(flow, input['value'], 'U')
            else:
                raise NotImplementedError('compute_checksum - tarefa 14/15/16')

        append(flow, checksum['target'], 'D')
