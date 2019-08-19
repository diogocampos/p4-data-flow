from collections import defaultdict


class DataFlow:
    def __init__(self):
        node = _Node()
        self._fields = defaultdict(list)  # header name -> field names
        self._initial_node = node
        self._current_node = node
        self._nodes = { node.key: node }  # key -> node
        self._transitions = defaultdict(list)  # node -> nodes

    def set_current_node(self, key):
        self._current_node = self._nodes.setdefault(key, _Node(key))

    def declare(self, field):
        header_name, field_name = field
        if field_name not in self._fields[header_name]:
            self._fields[header_name].append(field_name)

    def define(self, field): self._current_node.define(field)
    def use(self, field): self._current_node.use(field)

    def define_all(self, header_name):
        for field_name in self._fields[header_name]:
            self._current_node.define([header_name, field_name])

    def set_transitions(self, keys):
        transitions = self._transitions[self._current_node]
        for key in keys:
            transitions.append(self._nodes.setdefault(key, _Node(key)))

    def _all_paths(self):
        yield from self._visit(self._initial_node, [])

    def _visit(self, node, path):
        next_nodes = self._transitions.get(node)
        if next_nodes:
            for next_node in next_nodes:
                yield from self._visit(next_node, path + [node])
        else:
            yield path + [node]

    def format_output(self, omit_empty=False):
        parts = []
        for path in self._all_paths():
            parts.append(' -> '.join(node.key or 'null' for node in path))
            parts.append(self._format_path(path, omit_empty))
        return '\n\n'.join(parts)

    def _format_path(self, path, omit_empty):
        lines = []

        for header_name, field_names in self._fields.items():
            lines.append(f"    {header_name}")

            for field_name in field_names:
                sequences = (node.get(header_name, field_name) for node in path)
                parts = (''.join(seq) for seq in sequences if len(seq) > 0)
                string = ' '.join(parts)
                if omit_empty and len(string) == 0: continue
                lines.append(f"        {field_name}: {string}")

        return '\n'.join(lines)


_DEFINE = 'D'
_USE = 'U'

class _Node:
    def __init__(self, key=''):
        self.key = key if key != '' else _key_generator.next()
        self._headers = defaultdict(lambda: defaultdict(list))

    def define(self, field): self._append(field, _DEFINE)
    def use(self, field): self._append(field, _USE)

    def _append(self, field, def_or_use):
        header_name, field_name = field
        self._headers[header_name][field_name].append(def_or_use)

    def get(self, header_name, field_name):
        return list(self._headers[header_name][field_name])


# Helpers

class _KeyGenerator:
    def __init__(self):
        self._counter = 0

    def next(self):
        key = str(self._counter)
        self._counter += 1
        return key

_key_generator = _KeyGenerator()
