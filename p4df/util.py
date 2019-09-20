import sys


def find(iterable, **kwargs):
    for item in iterable:
        if all(item[key] == value for key, value in kwargs.items()):
            return item


def not_implemented(flow, key, value):
    print(f'[{flow.current_key}] not implemented: {key} == {repr(value)}',
        file=sys.stderr)


def operation(flow, node, action=None):
    if node is None: return

    if node['type'] == 'field':
        field = node['value']
        flow.use(field)

    elif node['type'] == 'runtime_data':
        index = node['value']
        data = action['runtime_data'][index]
        flow.use([action['name'], data['name']])

    elif node['type'] == 'expression':
        expression = node['value']
        if 'type' in expression:
            operation(flow, expression, action)
        else:
            left = expression['left']
            right = expression['right']
            cond = expression['cond'] if 'cond' in expression else None
            for part in (cond, left, right):
                operation(flow, part, action)


class BreadthFirstSearch:
    def __init__(self, first):
        self._queue = [first] if first is not None else []
        self._visited = []

    def __iter__(self):
        while len(self._queue) > 0:
            item = self._queue.pop(0)
            if item in self._visited: continue
            self._visited.append(item)
            yield item

    def enqueue(self, items):
        self._queue.extend(i for i in items if i is not None)
