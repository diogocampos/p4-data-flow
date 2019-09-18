from .util import find, not_implemented

def do_compute_checksum(p4, flow):
    flow.push_node('compute_checksum')

    for checksum in p4['checksums']:
        calculation = find(p4['calculations'], name=checksum['calculation'])

        for input in calculation['input']:
            if input['type'] == 'field':
                flow.use(input['value'])
            else:
                not_implemented('type', input['type'])

        flow.define(checksum['target'])
