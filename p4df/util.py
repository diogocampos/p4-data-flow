
def operation(node, flow):
    if node is None: return

    if node['type'] == 'field':
        append(flow, node['value'], 'U')

    elif node['type'] == 'expression':
        _expression(node['value'], flow)


def _expression(expr, flow):
    left = expr['left']
    right = expr['right']
    cond = expr['cond'] if 'cond' in expr else None

    for part in (left, right, cond):
        operation(part, flow)


def append(flow, field, du):
    header_name, field_name = field
    if field_name == '$valid$': return

    flow[header_name][field_name].append(du)


def find(iterable, predicate):
    for item in iterable:
        if predicate(item): return item
