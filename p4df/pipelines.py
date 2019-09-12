from .util import BreadthFirstSearch, find, operation


def do_pipelines(p4, flow):
    _pipeline('ingress', p4, flow)
    _pipeline('egress', p4, flow)


def _pipeline(pipeline_name, p4, flow):
    pipeline = find(p4['pipelines'], name=pipeline_name)
    bfs = BreadthFirstSearch(pipeline['init_table'])
    flow.set_prefix(pipeline['name'])
    flow.add_transitions([pipeline['init_table']])

    for table_name in bfs:
        table = find(pipeline['tables'], name=table_name)
        flow.set_current_node(table_name)

        if table:
            assert len(table['key']) > 0
            key = table['key'][0]

            if key['match_type'] == 'valid':
                raise NotImplementedError('pipelines - tarefa 2')

            flow.use(key['target'])

            # match
            actions = [
                (True, find(p4['actions'], name=action_name))
                for action_name in table['actions']]

            # no match
            actions.append(
                (False, find(p4['actions'], id=table['default_entry']['action_id']))
                )

            for matched, action in actions:
                match = 'Match' if matched else 'NoMatch'
                flow.push_node(f"{table['name']}/{match}/{action['name']}")

                flow.declare_header(action['name'])
                for item in action['runtime_data']:
                    flow.param([action['name'], item['name']])

                for primitive in action['primitives']:
                    if primitive['op'] == 'assign':
                        left, right = primitive['parameters']

                        operation(flow, right, action)

                        if left['type'] == 'field':
                            field = left['value']
                            flow.define(field)
                        elif left['type'] == 'runtime_data':
                            index = left['value']
                            data = action['runtime_data'][index]
                            flow.define([action['name'], data['name']])
                        else:
                            raise NotImplementedError('pipelines - tarefa 7')

                    #else:
                    #    raise NotImplementedError('pipelines - tarefa 3/4')

                next_tables = [table['next_tables'][action['name']]]
                flow.add_transitions(next_tables)
                bfs.enqueue(next_tables)
                flow.set_current_node(table['name'])

        else:
            conditional = find(pipeline['conditionals'], name=table_name)

            operation(flow, conditional['expression'])

            next_tables = [conditional['true_next'], conditional['false_next']]
            flow.add_transitions(next_tables)
            bfs.enqueue(next_tables)

    flow.set_current_node(None)
    flow.clear_prefix()
