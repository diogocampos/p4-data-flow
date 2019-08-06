#!/usr/bin/env python3

import json
import os

from p4df.compute_checksum import do_compute_checksum
from p4df.headers import do_headers
from p4df.parsers import do_parsers
from p4df.pipelines import do_pipelines


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
    do_pipelines(p4, flow)
    do_compute_checksum(p4, flow)
    return flow


def output(flow):
    for header_name, header in flow.items():
        print(f"{header_name}:")
        for field_name, sequence in header.items():
            if len(sequence) == 0: continue
            print(f"  {field_name}:")
            for du, (filename, function, lineno) in sequence:
                print(f"    {du} ({os.path.basename(filename)}:{function}:{lineno})")


if __name__ == '__main__':
    import sys
    result = main(sys.argv)
    sys.exit(result)
