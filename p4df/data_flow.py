from collections import defaultdict


class DataFlow:
    def __init__(self):
        node = Node()
        self._fields = defaultdict(list) # header name -> field names
        self._initial_node = node
        self._current_node = node
        self._nodes = defaultdict(Node) # key -> node
        self._transitions = defaultdict(list) # node -> nodes

    def set_current_node(self, key):
        self._current_node = self._nodes[key]

    def declare(self, field):
        header_name, field_name = field
        if field_name not in self._fields[header_name]:
            self._fields[header_name].append(field_name)

    def define(self, field): self._current_node.define(field)
    def use(self, field): self._current_node.use(field)

    def define_all(self, header_name):
        for field_name in self._initial_node._headers[header_name]:
            self._current_node.define([header_name, field_name])

    def set_transitions(self, keys):
        for key in keys:
            node = self._nodes[key]
            self._transitions[self._current_node].append(node)


DEFINE = 'D'
USE = 'U'

class Node:
    def __init__(self):
        self._headers = defaultdict(lambda: defaultdict(list))

    def define(self, field): self._append(field, DEFINE)
    def use(self, field): self._append(field, USE)

    def _append(self, field, def_or_use):
        header_name, field_name = field
        self._headers[header_name][field_name].append(def_or_use)


def format_output(flow, omit_empty=False):
    lines = []

    for header_name, field_names in flow._fields.items():
        lines.append(f"{header_name}:")

        for field_name in field_names:
            sequence = flow._current_node._headers[header_name][field_name]
            if omit_empty and len(sequence) == 0: continue
            lines.append(f"    {field_name}: {''.join(sequence)}")

    return '\n'.join(lines)
