#!/usr/bin/env python3

import json

from p4df.headers import do_headers
from p4df.parsers import do_parsers
from p4df.ingress import do_ingress


def main(argv):
    filename = argv[1]

    with open(filename, 'r') as fp:
        p4 = json.load(fp)

    flow = get_flow(p4)
    output(flow)


def get_flow(p4):
    flow = {}
    do_headers(p4, flow)
    do_parsers(p4, flow)
    do_ingress(p4, flow)
    return flow


def output(flow):
    for header_name, header in flow.items():
        print(f'{header_name}:')
        for field_name, sequence in header.items():
            print(f"    {field_name}: {''.join(sequence)}")


if __name__ == '__main__':
    import sys
    result = main(sys.argv)
    sys.exit(result)
