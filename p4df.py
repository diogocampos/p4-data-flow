#!/usr/bin/env python3

import argparse
import json

from p4df.compute_checksum import do_compute_checksum
from p4df.data_flow import DataFlow
from p4df.deparsers import do_deparsers
from p4df.headers import do_headers
from p4df.parsers import do_parsers
from p4df.pipelines import do_pipelines


def main(argv):
    args = parse_argv(argv)

    with args.jsonfile:
        p4 = json.load(args.jsonfile)

    flow = get_flow(p4)
    for result in flow.formatted_results(verbose=args.verbose):
        print('', result, sep='\n')


def parse_argv(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonfile', type=argparse.FileType('r'))
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser.parse_args(argv[1:])


def get_flow(p4):
    flow = DataFlow()
    do_headers(p4, flow)
    do_parsers(p4, flow)
    do_pipelines(p4, flow)
    do_compute_checksum(p4, flow)
    do_deparsers(p4, flow)
    return flow


if __name__ == '__main__':
    import sys
    result = main(sys.argv)
    sys.exit(result)
