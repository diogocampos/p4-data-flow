#!/usr/bin/env python3

from pprint import pprint
import json


def main(argv):
    filename = argv[1]

    with open(filename, 'r') as fp:
        p4 = json.load(fp)

    flow = get_flow(p4)
    pprint(flow)


def get_flow(p4):
    flow = {}
    do_headers(p4, flow)
    do_parsers(p4, flow)
    return flow


def do_headers(p4, flow):
    for header in p4['headers']:
        header_type = find(
            p4['header_types'],
            lambda item: item['name'] == header['header_type'],
        )

        fields = {}
        for field_name, *_ in header_type['fields']:
            fields[field_name] = []

        flow[header['name']] = fields


def do_parsers(p4, flow):
    parser = p4['parsers'][0]
    state = find(
        parser['parse_states'],
        lambda state: state['name'] == parser['init_state'],
    )

    while state is not None:
        print('STATE:', state['name'])

        op, *_ = state['parser_ops']
        if op['op'] != 'extract':
            raise NotImplementedError(f"op: {op['op']}")

        param, = op['parameters']
        if param['type'] != 'regular':
            raise NotImplementedError(f"parameter type: {param['type']}")

        sequence = flow[param['value']]
        for seq in sequence.values(): seq.append('D')

        for tk in state['transition_key']:
            if tk['type'] != 'field':
                raise NotImplementedError(f"transition_key type: {tk['type']}")

            header, field = tk['value']
            flow[header][field].append('U')

        for transition in state['transitions']:
            if 'type' not in transition:
                break
            elif transition['type'] == 'hexstr':
                # if transition['value'] == vtf: break  # ???
                break

        next_state = transition['next_state']
        if next_state is None: break

        state = find(
            parser['parse_states'],
            lambda state: state['name'] == next_state
        )


def find(list, predicate):
    for item in list:
        if predicate(item): return item


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
