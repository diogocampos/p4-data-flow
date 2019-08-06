import inspect
import os

def operation(flow, node, action=None):
    if node is None: return

    if node['type'] == 'field':
        field = node['value']
        append(flow, field, 'U')

    elif node['type'] == 'runtime_data':
        index = node['value']
        data_name = action['runtime_data'][index]['name']
        append(flow, [action['name'], data_name], 'U')

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


def append(flow, field, du):
    header_name, field_name = field

    if field_name not in flow[header_name]:
        flow[header_name][field_name] = []

    flow[header_name][field_name].append((du, _caller_info()))


def find(iterable, **kwargs):
    for item in iterable:
        if all(item[key] == value for key, value in kwargs.items()):
            return item


def _caller_info():
  caller_frame_record = inspect.stack()[2]
  frame = caller_frame_record[0]
  info = inspect.getframeinfo(frame)
  return (info.filename, info.function, info.lineno)
