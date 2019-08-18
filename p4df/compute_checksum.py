from .util import find

def do_compute_checksum(p4, flow):
    for checksum in p4['checksums']:
        calculation = find(p4['calculations'], name=checksum['calculation'])

        for input in calculation['input']:
            if input['type'] == 'field':
                flow.use(input['value'])
            else:
                raise NotImplementedError('compute_checksum - tarefa 14/15/16')

        flow.define(checksum['target'])
