from .util import find


def do_headers(p4, flow):
    for header in p4['headers']:
        header_type = find(
            p4['header_types'],
            lambda item: item['name'] == header['header_type'],
        )

        fields = {}
        for field_name, *_ in header_type['fields']:
            fields[field_name] = []

        flow[header['name']] = fields
