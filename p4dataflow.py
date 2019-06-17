#!/usr/bin/env python3

import json


def main(argv):
    filename = argv[1]

    with open(filename, 'r') as fp:
        p4 = json.load(fp)

    flow = get_flow(p4)
    output(flow)


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
    parser = p4['parsers'][0]  # pode haver mais de um ???
    state = find(
        parser['parse_states'],
        lambda state: state['name'] == parser['init_state'],
    )

    while state is not None:
        op, *_ = state['parser_ops']

        if op['op'] == 'extract':
            op_extract(op, flow)
        elif op['op'] == 'set':
            op_set(op, flow)
        elif op['op'] == 'verify':
            op_verify(op, flow)
        else:
            raise NotImplementedError(f"op: {op['op']}")

        if len(state['transition_key']) != 1:
            raise NotImplementedError(f'Multiple/missing transition_key items')

        tk, = state['transition_key']
        transition = None

        if tk['type'] == 'field':
            append(flow, tk['value'], 'U')

            #vtk = valor de tk['value']  # ???

            for transition in state['transitions']:
                if 'type' not in transition or transition['type'] == 'default':
                    break
                elif transition['type'] == 'hexstr':
                    # if transition['value'] == vtk: break  # ???
                    pass

        else:
            raise NotImplementedError(f"transition_key type: {tk['type']}")

        next_state = transition['next_state']
        if next_state is None: break

        state = find(
            parser['parse_states'],
            lambda state: state['name'] == next_state
        )


def op_extract(op, flow):
    param, = op['parameters']

    if param['type'] == 'regular':
        sequences = flow[param['value']]
        for seq in sequences.values(): seq.append('D')

    else:
        raise NotImplementedError(f"parameter type: {param['type']}")


def op_set(op, flow):
    left, right = op['parameters']
    append(flow, left['value'], 'D')
    operation(right, flow)


def op_verify(op, flow):
    assertion, errno = op['parameters']
    operation(assertion, flow)
    operation(errno, flow)


def operation(node, flow):
    if node is None: return

    if node['type'] == 'field':
        append(flow, node['value'], 'U')

    elif node['type'] == 'expression':
        expression(node['value'], flow)


def expression(expr, flow):
    left = expr['left']
    right = expr['right']
    cond = expr['cond'] if 'cond' in expr else None

    for part in (left, right, cond):
        operation(part, flow)


def append(flow, field, du):
    header_name, field_name = field
    flow[header_name][field_name].append(du)


def find(iterable, predicate):
    for item in iterable:
        if predicate(item): return item


def output(flow):
    for header_name, header in flow.items():
        print(f'{header_name}:')
        for field_name, sequence in header.items():
            print(f"    {field_name}: {''.join(sequence)}")


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
