from .util import append, find, operation


def do_parsers(p4, flow):
    parser = p4['parsers'][0]  # pode haver mais de um ???
    state = find(parser['parse_states'], name=parser['init_state'])

    while state is not None:
        op = state['parser_ops'][0]

        if op['op'] == 'extract':
            _extract(op, flow)
        elif op['op'] == 'set':
            _set(op, flow)
        elif op['op'] == 'verify':
            _verify(op, flow)
        else:
            raise NotImplementedError('parsers - tarefa 2/5/6')

        assert len(state['transition_key']) == 1

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
            raise NotImplementedError('parsers - tarefa 9/10/11')

        next_state = transition['next_state']
        if next_state is None: break

        state = find(parser['parse_states'], name=next_state)


def _extract(op, flow):
    param, = op['parameters']

    if param['type'] == 'regular':
        sequences = flow[param['value']]
        for seq in sequences.values(): seq.append('D')

    else:
        raise NotImplementedError('parsers - tarefa 7/8')


def _set(op, flow):
    left, right = op['parameters']
    operation(flow, right)
    append(flow, left['value'], 'D')


def _verify(op, flow):
    assertion, errno = op['parameters']
    operation(flow, assertion)
    operation(flow, errno)
