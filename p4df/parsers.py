from .util import append, find, operation


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
