from .util import find


def do_headers(p4, flow):
    for header in p4['headers']:
        header_type = find(p4['header_types'], name=header['header_type'])

        flow.declare_header(header['name'])
        for field_name, *_ in header_type['fields']:
            flow.declare([header['name'], field_name])
