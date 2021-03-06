from .util import BreadthFirstSearch, find, not_implemented, operation


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
            if len(table['key']) > 0:
                key = table['key'][0]
                if key['match_type'] == 'valid':
                    not_implemented(flow, 'match_type', 'valid')
                else:
                    flow.use(key['target'])

            # match
            actions = [find(p4['actions'], name=action_name)
                for action_name in table['actions']]

            # no match
            if 'default_entry' in table:
                default_action_id = table['default_entry']['action_id']
                default_action = find(p4['actions'], id=default_action_id)
                if default_action not in actions: actions.append(default_action)

            for action in actions:
                flow.push_node(f"{table['name']}/{action['name']}")

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
                            not_implemented(flow, 'type', left['type'])

                    elif primitive['op'] == 'drop':
                        flow.drop(['standard_metadata', 'egress_spec'])

                    else:
                        not_implemented(flow, 'op', primitive['op'])

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
