from collections import defaultdict


class DataFlow:
    def __init__(self):
        node = _Node('0')
        self._fields = defaultdict(list)  # header name -> field names
        self._initial_node = node
        self._current_node = node
        self._nodes = { node.key: node }  # key -> node
        self._transitions = defaultdict(list)  # node -> nodes
        self._prefix = None

    @property
    def current_key(self):
        return self._current_node.key

    def set_current_node(self, key):
        key = self._normalize_key(key)
        self._current_node = self._nodes.setdefault(key, _Node(key))

    def add_transitions(self, keys):
        transitions = self._transitions[self._current_node]
        for key in keys:
            key = self._normalize_key(key)
            node = self._nodes.setdefault(key, _Node(key))
            if node not in transitions: transitions.append(node)

    def push_node(self, key):
        self.add_transitions([key])
        self.set_current_node(key)

    def _normalize_key(self, key):
        if key is None: key = 'null'
        if self._prefix: key = f'{self._prefix}/{key}'
        return key

    def set_prefix(self, prefix):
        self._prefix = prefix

    def clear_prefix(self):
        self._prefix = None

    def declare_header(self, header_name):
        field_names = self._fields[header_name]

    def declare(self, field):
        header_name, field_name = field
        if field_name not in self._fields[header_name]:
            self._fields[header_name].append(field_name)

    def define(self, field):
        self.declare(field)
        self._current_node.define(field)

    def param(self, field):
        self.declare(field)
        self._current_node.param(field)

    def use(self, field):
        self.declare(field)
        self._current_node.use(field)

    def define_all(self, header_name):
        for field_name in self._fields[header_name]:
            self._current_node.define([header_name, field_name])

    def use_all(self, header_name):
        for field_name in self._fields[header_name]:
            self._current_node.use([header_name, field_name])

    def _all_paths(self, verbose):
        yield from self._visit(self._initial_node, [], verbose)

    def _visit(self, node, subpath, verbose):
        if node in subpath:
            print('\nCYCLE:', ' -> '.join(n.key for n in subpath + [node]))
            return

        if not verbose and not self._is_feasible_subpath(subpath, node):
            return

        path = subpath + [node]
        next_nodes = self._transitions.get(node)
        if next_nodes:
            for next_node in next_nodes:
                yield from self._visit(next_node, path, verbose)
        else:
            yield path

    def _is_feasible_subpath(self, subpath, last_node):
        for header_name, field_names in self._fields.items():
            if 'U' not in last_node.get(header_name, '$valid$'): continue

            for field_name in field_names:
                if field_name == '$valid$': continue
                seq = ''.join(n.get(header_name, field_name) for n in subpath)
                if 'D' not in seq and 'P' not in seq: return False

        return True

    def formatted_results(self, verbose=False):
        for path in self._all_paths(verbose):
            yield self._format_path(path, verbose)

    def _format_path(self, path, verbose):
        lines = [' -> '.join(node.key for node in path)]

        for header_name, field_names in self._fields.items():
            section = [f'    {header_name}']

            for field_name in field_names:
                sequences = (node.get(header_name, field_name) for node in path)
                if verbose:
                    keys = (node.key for node in path)
                    parts = (f'[{key}] {seq}'
                        for key, seq in zip(keys, sequences) if len(seq) > 0)
                    string = ', '.join(parts)
                else:
                    parts = (seq for seq in sequences if len(seq) > 0)
                    string = ''.join(parts)

                if not verbose and len(string) == 0: continue
                section.append(f'        {field_name}: {string}')

            if not verbose and len(section) == 1: continue
            lines.extend(section)

        return '\n'.join(lines)


class _Node:
    def __init__(self, key):
        self.key = key
        self._headers = defaultdict(lambda: defaultdict(list))

    def define(self, field): self._append(field, 'D')
    def param(self, field): self._append(field, 'P')
    def use(self, field): self._append(field, 'U')

    def _append(self, field, def_or_use):
        header_name, field_name = field
        self._headers[header_name][field_name].append(def_or_use)

    def get(self, header_name, field_name):
        return ''.join(self._headers[header_name][field_name])
