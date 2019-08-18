from .util import find, operation


def do_pipelines(p4, flow):
    _pipeline('ingress', p4, flow)
    _pipeline('egress', p4, flow)


def _pipeline(pipeline_name, p4, flow):
    pipeline = find(p4['pipelines'], name=pipeline_name)
    table_name = pipeline['init_table']

    while table_name is not None:
        table = find(pipeline['tables'], name=table_name)

        if table is not None:
            # TODO table['key'] pode ser uma lista vazia (mri.json)
            if len(table['key']) == 0: break
            key = table['key'][0]
            if key['match_type'] == 'valid':
                raise NotImplementedError('pipelines - tarefa 2')

            flow.use(key['target'])
            # match_type true/false ??

            for action_name in table['actions']:
                action = find(p4['actions'], name=action_name)

                for item in action['runtime_data']:
                    flow.declare([action['name'], item['name']])

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

            break

        else:  # table não localizada
            conditional = find(pipeline['conditionals'], name=table_name)

            operation(flow, conditional['expression'])

            table_name = conditional['true_next']
            # TODO conditional['false_next']
