#!/usr/bin/env python3

import json

from p4df.compute_checksum import do_compute_checksum
from p4df.data_flow import DataFlow, format_output
from p4df.headers import do_headers
from p4df.parsers import do_parsers
from p4df.pipelines import do_pipelines


def main(argv):
    filename = argv[1]

    with open(filename, 'r') as fp:
        p4 = json.load(fp)

    flow = get_flow(p4)
    print(format_output(flow, omit_empty=True))


def get_flow(p4):
    flow = DataFlow()
    do_headers(p4, flow)
    do_parsers(p4, flow)
    do_pipelines(p4, flow)
    do_compute_checksum(p4, flow)
    return flow


if __name__ == '__main__':
    import sys
    result = main(sys.argv)
    sys.exit(result)
