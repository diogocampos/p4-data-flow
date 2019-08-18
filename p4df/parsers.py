from .util import BreadthFirstSearch, find, operation


def do_parsers(p4, flow):
    parser = p4['parsers'][0]
    bfs = BreadthFirstSearch(parser['init_state'])
    flow.set_transitions([parser['init_state']])

    for state_name in bfs:
        state = find(parser['parse_states'], name=state_name)
        flow.set_current_node(state_name)

        for op in state['parser_ops']:
            if op['op'] == 'extract': _extract(op, flow)
            elif op['op'] == 'set': _set(op, flow)
            elif op['op'] == 'verify': _verify(op, flow)
            else: raise NotImplementedError('parsers - tarefa 2/5/6')

        for tk in state['transition_key']:
            if tk['type'] == 'field':
                flow.use(tk['value'])

        next_states = [t['next_state'] for t in state['transitions']]
        flow.set_transitions(next_states)
        bfs.enqueue(name for name in next_states if name is not None)

    flow.set_current_node(None)


def _extract(op, flow):
    param, = op['parameters']

    if param['type'] == 'regular':
        header_name = param['value']
        flow.define_all(header_name)

    else:
        raise NotImplementedError('parsers - tarefa 7/8')


def _set(op, flow):
    left, right = op['parameters']
    operation(flow, right)
    flow.define(left['value'])


def _verify(op, flow):
    assertion, errno = op['parameters']
    operation(flow, assertion)
    operation(flow, errno)
